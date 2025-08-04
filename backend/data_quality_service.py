#!/usr/bin/env python3
"""
Data Quality Service for validating and cleaning government documents
Ensures high-quality data before indexing and search
"""
import asyncio
import json
import re
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, date
import aiosqlite
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    processed_document: Optional[Dict] = None

class DataQualityService:
    """Ensures high-quality data before indexing"""
    
    def __init__(self):
        self.required_fields = ['identifier', 'title', 'full_text', 'document_type']
        self.valid_document_types = ['bill', 'executive_order', 'resolution', 'amendment']
        self.valid_statuses = [
            'introduced', 'passed_house', 'passed_senate', 'enacted', 'vetoed',
            'failed', 'withdrawn', 'active', 'inactive', 'signed'
        ]
    
    async def validate_and_process_document(self, raw_document: Dict) -> ValidationResult:
        """Validate and enhance document before database storage"""
        
        errors = []
        warnings = []
        
        try:
            # Step 1: Check required fields
            if not self._has_required_fields(raw_document):
                missing_fields = [field for field in self.required_fields if not raw_document.get(field)]
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")
                return ValidationResult(False, errors, warnings)
            
            # Step 2: Clean and normalize document
            processed_doc = self._clean_document(raw_document.copy())
            
            # Step 3: Validate document type
            if not self._validate_document_type(processed_doc):
                errors.append(f"Invalid document type: {processed_doc.get('document_type')}")
            
            # Step 4: Validate identifier format
            identifier_warnings = self._validate_identifier(processed_doc.get('identifier', ''))
            warnings.extend(identifier_warnings)
            
            # Step 5: Validate and normalize dates
            date_errors = self._validate_dates(processed_doc)
            errors.extend(date_errors)
            
            # Step 6: Clean and validate text content
            text_warnings = self._validate_text_content(processed_doc)
            warnings.extend(text_warnings)
            
            # Step 7: Normalize sponsor data
            processed_doc['sponsor'] = self._normalize_sponsor_data(processed_doc.get('sponsor'))
            
            # Step 8: Validate and clean metadata
            processed_doc['metadata'] = self._clean_metadata(processed_doc.get('metadata', {}))
            
            # Step 9: Generate summary if missing
            if not processed_doc.get('summary') and processed_doc.get('full_text'):
                processed_doc['summary'] = await self._generate_summary(processed_doc['full_text'])
                warnings.append("Generated summary from full text")
            
            # Step 10: Validate status
            if processed_doc.get('status') and processed_doc['status'].lower() not in self.valid_statuses:
                warnings.append(f"Unknown status: {processed_doc['status']}")
            
            # Step 11: Add quality score
            processed_doc['quality_score'] = self._calculate_quality_score(processed_doc)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                processed_document=processed_doc if is_valid else None
            )
            
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            errors.append(f"Validation error: {str(e)}")
            return ValidationResult(False, errors, warnings)
    
    def _has_required_fields(self, doc: Dict) -> bool:
        """Check for required fields"""
        return all(doc.get(field) for field in self.required_fields)
    
    def _clean_document(self, doc: Dict) -> Dict:
        """Clean and normalize document data"""
        
        # Clean title
        if doc.get('title'):
            doc['title'] = self._clean_text(doc['title'])
            # Remove common prefixes that add no value
            doc['title'] = re.sub(r'^(A Bill |An Act )', '', doc['title'], flags=re.IGNORECASE)
        
        # Clean summary
        if doc.get('summary'):
            doc['summary'] = self._clean_text(doc['summary'])
        
        # Clean full text
        if doc.get('full_text'):
            doc['full_text'] = self._clean_full_text(doc['full_text'])
        
        # Normalize identifier
        if doc.get('identifier'):
            doc['identifier'] = self._normalize_identifier(doc['identifier'])
        
        # Normalize document type
        if doc.get('document_type'):
            doc['document_type'] = doc['document_type'].lower().strip()
        
        # Normalize status
        if doc.get('status'):
            doc['status'] = doc['status'].lower().strip()
        
        return doc
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
    
    def _clean_full_text(self, text: str) -> str:
        """Clean full text with additional processing"""
        text = self._clean_text(text)
        
        # Remove common legislative artifacts
        text = re.sub(r'<<.*?>>', '', text)  # Remove <<NOTE>> tags
        text = re.sub(r'\[\[Page \d+\]\]', '', text)  # Remove page markers
        text = re.sub(r'<all>', '', text, flags=re.IGNORECASE)  # Remove <all> tags
        
        # Normalize section headers
        text = re.sub(r'\n\s*SEC\.\s*(\d+)', r'\n\nSEC. \1', text)
        text = re.sub(r'\n\s*SECTION\s*(\d+)', r'\n\nSECTION \1', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _normalize_identifier(self, identifier: str) -> str:
        """Normalize document identifier"""
        if not identifier:
            return ""
        
        identifier = identifier.upper().strip()
        
        # Standardize format: HR-123, S-456, EO-789
        identifier = re.sub(r'H\.?R\.?\s*(\d+)', r'HR-\1', identifier)
        identifier = re.sub(r'S\.?\s*(\d+)', r'S-\1', identifier)
        identifier = re.sub(r'EXECUTIVE ORDER\s*(\d+)', r'EO-\1', identifier)
        identifier = re.sub(r'E\.?O\.?\s*(\d+)', r'EO-\1', identifier)
        
        return identifier
    
    def _validate_document_type(self, doc: Dict) -> bool:
        """Validate document type"""
        doc_type = doc.get('document_type', '').lower()
        return doc_type in self.valid_document_types
    
    def _validate_identifier(self, identifier: str) -> List[str]:
        """Validate identifier format"""
        warnings = []
        
        if not identifier:
            warnings.append("Missing document identifier")
            return warnings
        
        # Check for valid patterns
        valid_patterns = [
            r'^HR-\d+$',          # HR-123
            r'^S-\d+$',           # S-456
            r'^EO-\d+$',          # EO-789
            r'^H\.RES\.-\d+$',    # H.RES.-123
            r'^S\.RES\.-\d+$'     # S.RES.-456
        ]
        
        if not any(re.match(pattern, identifier) for pattern in valid_patterns):
            warnings.append(f"Unusual identifier format: {identifier}")
        
        return warnings
    
    def _validate_dates(self, doc: Dict) -> List[str]:
        """Validate and normalize date fields"""
        errors = []
        
        for date_field in ['introduced_date', 'last_action_date']:
            date_value = doc.get(date_field)
            
            if date_value:
                try:
                    # Try to parse various date formats
                    if isinstance(date_value, str):
                        # Common formats: YYYY-MM-DD, MM/DD/YYYY, etc.
                        if re.match(r'\d{4}-\d{2}-\d{2}', date_value):
                            parsed_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                        elif re.match(r'\d{2}/\d{2}/\d{4}', date_value):
                            parsed_date = datetime.strptime(date_value, '%m/%d/%Y').date()
                        elif re.match(r'\d{4}/\d{2}/\d{2}', date_value):
                            parsed_date = datetime.strptime(date_value, '%Y/%m/%d').date()
                        else:
                            # Try generic parsing
                            parsed_date = datetime.fromisoformat(date_value.replace('/', '-')).date()
                        
                        doc[date_field] = parsed_date.isoformat()
                    
                    elif isinstance(date_value, datetime):
                        doc[date_field] = date_value.date().isoformat()
                    elif isinstance(date_value, date):
                        doc[date_field] = date_value.isoformat()
                
                except (ValueError, TypeError) as e:
                    errors.append(f"Invalid {date_field}: {date_value}")
                    doc[date_field] = None
        
        # Validate date logic
        if doc.get('introduced_date') and doc.get('last_action_date'):
            try:
                intro_date = datetime.fromisoformat(doc['introduced_date']).date()
                action_date = datetime.fromisoformat(doc['last_action_date']).date()
                
                if action_date < intro_date:
                    errors.append("Last action date cannot be before introduced date")
            except:
                pass  # Already handled above
        
        return errors
    
    def _validate_text_content(self, doc: Dict) -> List[str]:
        """Validate text content quality"""
        warnings = []
        
        # Check title length
        title = doc.get('title', '')
        if len(title) < 10:
            warnings.append("Title is very short")
        elif len(title) > 500:
            warnings.append("Title is unusually long")
        
        # Check summary
        summary = doc.get('summary', '')
        if summary and len(summary) < 50:
            warnings.append("Summary is very short")
        
        # Check full text length
        full_text = doc.get('full_text', '')
        if len(full_text) < 100:
            warnings.append("Full text is very short")
        elif len(full_text) > 1000000:  # 1MB
            warnings.append("Full text is extremely long")
        
        # Check for placeholder text
        placeholder_patterns = [
            r'lorem ipsum',
            r'placeholder',
            r'TODO',
            r'FIXME',
            r'test document'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                warnings.append(f"Document may contain placeholder text: {pattern}")
        
        return warnings
    
    def _normalize_sponsor_data(self, sponsor_data: Any) -> Optional[Dict]:
        """Normalize sponsor information"""
        if not sponsor_data:
            return None
        
        try:
            # Handle string JSON
            if isinstance(sponsor_data, str):
                try:
                    sponsor_data = json.loads(sponsor_data)
                except json.JSONDecodeError:
                    # Treat as simple name
                    return {"full_name": sponsor_data.strip()}
            
            # Handle dictionary
            if isinstance(sponsor_data, dict):
                normalized = {}
                
                # Normalize name fields
                if sponsor_data.get('full_name'):
                    normalized['full_name'] = sponsor_data['full_name'].strip()
                elif sponsor_data.get('first_name') and sponsor_data.get('last_name'):
                    normalized['full_name'] = f"{sponsor_data['first_name']} {sponsor_data['last_name']}".strip()
                
                # Normalize party
                if sponsor_data.get('party'):
                    party = sponsor_data['party'].strip().upper()
                    # Standardize party names
                    party_map = {
                        'D': 'Democratic', 'DEM': 'Democratic', 'DEMOCRAT': 'Democratic',
                        'R': 'Republican', 'REP': 'Republican', 'GOP': 'Republican',
                        'I': 'Independent', 'IND': 'Independent'
                    }
                    normalized['party'] = party_map.get(party, party)
                
                # Normalize state
                if sponsor_data.get('state'):
                    normalized['state'] = sponsor_data['state'].strip().upper()
                
                # Add other fields
                for field in ['bioguide_id', 'district', 'chamber']:
                    if sponsor_data.get(field):
                        normalized[field] = str(sponsor_data[field]).strip()
                
                return normalized if normalized else None
            
            # Handle list (multiple sponsors)
            if isinstance(sponsor_data, list) and sponsor_data:
                # For now, just take the first sponsor
                return self._normalize_sponsor_data(sponsor_data[0])
            
        except Exception as e:
            logger.warning(f"Failed to normalize sponsor data: {e}")
        
        return None
    
    def _clean_metadata(self, metadata: Any) -> Dict:
        """Clean and validate metadata"""
        if not metadata:
            return {}
        
        try:
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            if not isinstance(metadata, dict):
                return {}
            
            cleaned = {}
            
            # Keep only valid metadata fields
            valid_fields = [
                'committee', 'subcommittee', 'cosponsors', 'subjects',
                'actions', 'amendments', 'votes', 'related_bills',
                'congress', 'session', 'chamber'
            ]
            
            for field in valid_fields:
                if field in metadata and metadata[field]:
                    cleaned[field] = metadata[field]
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Failed to clean metadata: {e}")
            return {}
    
    async def _generate_summary(self, full_text: str, max_length: int = 300) -> str:
        """Generate basic summary from full text"""
        if not full_text or len(full_text) < 100:
            return ""
        
        # Simple extractive summary - take first few sentences
        sentences = re.split(r'[.!?]+', full_text)
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Skip very short sentences (likely fragments)
            if len(sentence) < 20:
                continue
            
            # Check if adding this sentence would exceed max length
            if current_length + len(sentence) > max_length:
                break
            
            summary_sentences.append(sentence)
            current_length += len(sentence)
            
            # Stop after 3-4 sentences
            if len(summary_sentences) >= 3:
                break
        
        summary = '. '.join(summary_sentences)
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _calculate_quality_score(self, doc: Dict) -> float:
        """Calculate document quality score (0.0 - 1.0)"""
        score = 0.0
        
        # Title quality (20%)
        title = doc.get('title', '')
        if title:
            if 50 <= len(title) <= 200:
                score += 0.2
            elif 20 <= len(title) <= 300:
                score += 0.15
            else:
                score += 0.1
        
        # Summary quality (20%)
        summary = doc.get('summary', '')
        if summary:
            if 100 <= len(summary) <= 500:
                score += 0.2
            elif 50 <= len(summary) <= 800:
                score += 0.15
            else:
                score += 0.1
        
        # Full text quality (30%)
        full_text = doc.get('full_text', '')
        if full_text:
            if len(full_text) >= 500:
                score += 0.3
            elif len(full_text) >= 200:
                score += 0.2
            else:
                score += 0.1
        
        # Metadata completeness (15%)
        if doc.get('sponsor'):
            score += 0.05
        if doc.get('introduced_date'):
            score += 0.05
        if doc.get('status'):
            score += 0.05
        
        # Identifier format (10%)
        identifier = doc.get('identifier', '')
        if re.match(r'^(HR|S|EO)-\d+$', identifier):
            score += 0.1
        elif identifier:
            score += 0.05
        
        # Date completeness (5%)
        if doc.get('last_action_date'):
            score += 0.05
        
        return min(score, 1.0)
    
    async def validate_database_documents(self, batch_size: int = 100) -> Dict:
        """Validate all documents in the database"""
        
        DATABASE_PATH = "./governmentgpt_local.db"
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get total count
            cursor = await db.execute("SELECT COUNT(*) FROM documents")
            total_docs = (await cursor.fetchone())[0]
            
            if total_docs == 0:
                return {"total": 0, "valid": 0, "invalid": 0, "warnings": 0}
            
            logger.info(f"🔍 Validating {total_docs} documents in database...")
            
            valid_count = 0
            invalid_count = 0
            warning_count = 0
            issues = []
            
            # Process in batches
            for offset in range(0, total_docs, batch_size):
                cursor = await db.execute("""
                    SELECT id, identifier, title, summary, full_text, document_type,
                           status, introduced_date, last_action_date, doc_metadata
                    FROM documents
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))
                
                batch = await cursor.fetchall()
                
                for row in batch:
                    doc_dict = {
                        'id': row[0],
                        'identifier': row[1],
                        'title': row[2],
                        'summary': row[3],
                        'full_text': row[4],
                        'document_type': row[5],
                        'status': row[6],
                        'introduced_date': row[7],
                        'last_action_date': row[8],
                        'metadata': row[9]
                    }
                    
                    result = await self.validate_and_process_document(doc_dict)
                    
                    if result.is_valid:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        issues.extend([f"{doc_dict['identifier']}: {error}" for error in result.errors])
                    
                    if result.warnings:
                        warning_count += 1
                
                if (offset // batch_size + 1) % 10 == 0:
                    logger.info(f"📈 Progress: {offset + len(batch)}/{total_docs} documents validated")
            
            logger.info(f"✅ Validation complete: {valid_count} valid, {invalid_count} invalid, {warning_count} with warnings")
            
            return {
                "total": total_docs,
                "valid": valid_count,
                "invalid": invalid_count,
                "warnings": warning_count,
                "issues": issues[:50]  # Limit to first 50 issues
            }

async def test_data_quality():
    """Test data quality service"""
    
    service = DataQualityService()
    
    # Test document
    test_doc = {
        "identifier": "hr 123",
        "title": "A Bill to improve infrastructure",
        "summary": "This bill provides funding for infrastructure improvements across the United States.",
        "full_text": "Be it enacted by the Senate and House of Representatives...",
        "document_type": "bill",
        "status": "introduced",
        "introduced_date": "2024-01-15",
        "sponsor": {"full_name": "John Doe", "party": "D", "state": "CA"}
    }
    
    print("🧪 Testing document validation...")
    result = await service.validate_and_process_document(test_doc)
    
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    if result.processed_document:
        print(f"Quality Score: {result.processed_document.get('quality_score', 0):.2f}")
        print(f"Processed Identifier: {result.processed_document.get('identifier')}")

if __name__ == "__main__":
    asyncio.run(test_data_quality())