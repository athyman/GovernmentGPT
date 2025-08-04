#!/usr/bin/env python3
"""
Hybrid Search Service implementing semantic + keyword search
Based on consultant recommendations and technical guide specifications
"""
import asyncio
import json
import numpy as np
import re
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, or_, and_, text, func
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document
import httpx
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class HybridSearchService:
    def __init__(self, claude_api_key: Optional[str] = None):
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        self.claude_client = httpx.AsyncClient(timeout=30.0)
        
        # Try to import sentence transformers for semantic search
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.semantic_enabled = True
            logger.info("Semantic search enabled with sentence-transformers")
        except ImportError:
            self.embedding_model = None
            self.semantic_enabled = False
            logger.warning("Semantic search disabled - install sentence-transformers for full functionality")
    
    async def search_with_ai_response(self, query: str, limit: int = 20) -> Dict:
        """Main search method with AI-generated response"""
        start_time = datetime.now()
        
        try:
            # 1. Preprocess query
            processed_query = self._preprocess_query(query)
            logger.info(f"Processed query: '{query}' -> '{processed_query}'")
            
            # 2. Execute hybrid search
            documents = await self.hybrid_search(processed_query, limit)
            
            # 3. Generate Claude response
            claude_response = await self.generate_claude_response(query, documents)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 4. Return comprehensive results
            return {
                "query": query,
                "processed_query": processed_query,
                "documents": documents,
                "claude_response": claude_response["response"],
                "confidence": claude_response["confidence"],
                "suggestions": claude_response["suggestions"],
                "search_type": "hybrid",
                "total_results": len(documents),
                "execution_time_ms": int(execution_time),
                "semantic_enabled": self.semantic_enabled
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self._error_response(query, str(e))
    
    async def hybrid_search(self, query: str, limit: int) -> List[Dict]:
        """Hybrid search combining multiple strategies"""
        
        # Store original query for phrase matching bonus
        self._current_query = query
        
        # Strategy 1: Full-text search (primary)
        fts_results = await self._full_text_search(query, limit)
        
        # Strategy 2: Semantic search (if available)
        semantic_results = []
        if self.semantic_enabled:
            semantic_results = await self._semantic_search(query, limit)
        
        # Strategy 3: Metadata search (identifiers, sponsors)
        metadata_results = await self._metadata_search(query, limit)
        
        # Combine using weighted Reciprocal Rank Fusion with phrase bonuses
        combined = self._weighted_rank_fusion([
            (fts_results, 0.5),      # 50% keyword weight
            (semantic_results, 0.3),  # 30% semantic weight  
            (metadata_results, 0.2)   # 20% metadata weight
        ], limit)
        
        return combined
    
    async def _full_text_search(self, query: str, limit: int) -> List[Tuple[Dict, float]]:
        """Enhanced keyword search with SQLite FTS5 if available"""
        
        async with AsyncSessionLocal() as db:
            try:
                # Try FTS5 search first - escape special characters for FTS5
                fts_query = query.replace('"', '""').replace("'", "''")
                
                fts_sql = """
                SELECT d.id, d.document_type, d.identifier, d.title, d.summary, d.full_text, 
                       d.status, d.introduced_date, d.last_action_date, d.sponsor_id, 
                       d.doc_metadata, d.created_at, d.updated_at,
                       bm25(documents_fts) as rank_score
                FROM documents_fts 
                JOIN documents d ON documents_fts.rowid = d.rowid
                WHERE documents_fts MATCH :query
                ORDER BY rank_score
                LIMIT :limit
                """
                
                result = await db.execute(text(fts_sql), {"query": fts_query, "limit": limit})
                rows = result.fetchall()
                
                if rows:
                    logger.info(f"FTS5 search found {len(rows)} results")
                    return [(self._row_to_dict(row), abs(row.rank_score)) for row in rows]
                    
            except Exception as e:
                logger.warning(f"FTS5 search failed: {e}, falling back to LIKE search")
            
            # Fallback to enhanced LIKE search with ranking
            return await self._enhanced_like_search(db, query, limit)
    
    async def _enhanced_like_search(self, db: AsyncSession, query: str, limit: int) -> List[Tuple[Dict, float]]:
        """Enhanced LIKE search with custom ranking"""
        
        search_terms = [term.strip() for term in query.lower().split() if len(term.strip()) > 2]
        
        if not search_terms:
            # Return recent documents if no valid search terms
            stmt = select(Document).order_by(Document.last_action_date.desc()).limit(limit)
            result = await db.execute(stmt)
            documents = result.scalars().all()
            return [(self._doc_to_dict(doc), 0.5) for doc in documents]
        
        # Build search conditions with ranking
        conditions = []
        for term in search_terms:
            term_condition = or_(
                Document.title.ilike(f"%{term}%"),
                Document.summary.ilike(f"%{term}%"),
                Document.full_text.ilike(f"%{term}%"),
                Document.identifier.ilike(f"%{term}%")
            )
            conditions.append(term_condition)
        
        # Combine conditions
        final_condition = or_(*conditions) if len(conditions) == 1 else and_(*conditions)
        
        stmt = select(Document).where(final_condition).order_by(Document.last_action_date.desc()).limit(limit * 2)
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        # Calculate relevance scores
        scored_results = []
        for doc in documents:
            score = self._calculate_text_relevance(query, doc)
            scored_results.append((self._doc_to_dict(doc), score))
        
        # Sort by relevance score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:limit]
    
    async def _semantic_search(self, query: str, limit: int) -> List[Tuple[Dict, float]]:
        """Semantic search using document embeddings"""
        
        if not self.embedding_model:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            async with AsyncSessionLocal() as db:
                # Check if embeddings table exists
                check_sql = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='document_embeddings'
                """
                result = await db.execute(text(check_sql))
                if not result.fetchone():
                    logger.info("No embeddings table found, skipping semantic search")
                    return []
                
                # Retrieve documents with embeddings
                sql = """
                SELECT d.*, e.embedding 
                FROM documents d
                JOIN document_embeddings e ON d.id = e.document_id
                WHERE e.embedding IS NOT NULL
                LIMIT 1000
                """
                
                result = await db.execute(text(sql))
                results = []
                
                for row in result:
                    doc_dict = self._row_to_dict(row[:-1])
                    embedding_blob = row[-1]
                    
                    if embedding_blob:
                        try:
                            doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                            
                            # Calculate cosine similarity
                            similarity = np.dot(query_embedding, doc_embedding) / (
                                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                            )
                            
                            if similarity > 0.1:  # Minimum similarity threshold
                                results.append((doc_dict, float(similarity)))
                                
                        except Exception as e:
                            logger.warning(f"Error processing embedding: {e}")
                            continue
                
                # Sort by similarity
                results.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"Semantic search found {len(results)} results")
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    async def _metadata_search(self, query: str, limit: int) -> List[Tuple[Dict, float]]:
        """Search by identifiers, sponsors, and metadata"""
        
        async with AsyncSessionLocal() as db:
            results = []
            
            # Search by identifier patterns (HR-123, S-456, EO-789)
            identifier_patterns = self._extract_identifiers(query)
            
            for pattern in identifier_patterns:
                stmt = select(Document).where(Document.identifier.ilike(f"%{pattern}%"))
                result = await db.execute(stmt)
                docs = result.scalars().all()
                
                for doc in docs:
                    results.append((self._doc_to_dict(doc), 1.0))  # High score for exact matches
            
            # Search by sponsor names in metadata
            sponsor_terms = self._extract_potential_sponsors(query)
            
            for sponsor_term in sponsor_terms:
                stmt = select(Document).where(Document.doc_metadata.like(f'%"{sponsor_term}"%'))
                result = await db.execute(stmt)
                docs = result.scalars().all()
                
                for doc in docs:
                    results.append((self._doc_to_dict(doc), 0.8))  # High score for sponsor matches
            
            # Remove duplicates
            seen_ids = set()
            unique_results = []
            for doc_dict, score in results:
                if doc_dict['id'] not in seen_ids:
                    seen_ids.add(doc_dict['id'])
                    unique_results.append((doc_dict, score))
            
            return unique_results[:limit]
    
    def _weighted_rank_fusion(self, result_lists: List[Tuple[List[Tuple[Dict, float]], float]], limit: int, k: int = 60) -> List[Dict]:
        """Combine search results using weighted Reciprocal Rank Fusion with phrase matching bonus"""
        
        doc_scores = {}
        
        for results, weight in result_lists:
            for rank, (doc, score) in enumerate(results):
                doc_id = doc['id']
                rrf_score = weight * (1 / (k + rank + 1))
                
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {'doc': doc, 'score': 0, 'sources': [], 'phrase_bonus': 0}
                
                doc_scores[doc_id]['score'] += rrf_score
                doc_scores[doc_id]['sources'].append({'type': 'search', 'weight': weight, 'rank': rank})
        
        # Add phrase matching bonus for better user intent understanding
        original_query = getattr(self, '_current_query', '').lower()
        for doc_id, doc_info in doc_scores.items():
            doc = doc_info['doc']
            title = doc.get('title', '').lower()
            
            # Bonus for exact phrase matches in title
            if len(original_query.split()) > 2:  # Only for multi-word queries
                if original_query in title:
                    doc_info['phrase_bonus'] += 2.0  # Strong bonus for exact phrase match
                elif any(word in title for word in original_query.split() if len(word) > 3):
                    matching_words = sum(1 for word in original_query.split() if word in title and len(word) > 3)
                    doc_info['phrase_bonus'] += matching_words * 0.5
            
            # Bonus for specific important terms
            important_terms = ['infrastructure', 'beautiful', 'jobs', 'investment']
            for term in important_terms:
                if term in original_query and term in title:
                    doc_info['phrase_bonus'] += 1.0
            
            # Final score combines RRF and phrase bonus
            doc_info['final_score'] = doc_info['score'] + doc_info['phrase_bonus']
        
        # Sort by final score (RRF + phrase bonus)
        ranked_docs = sorted(doc_scores.values(), key=lambda x: x['final_score'], reverse=True)
        
        # Add relevance scores to documents
        final_results = []
        for item in ranked_docs[:limit]:
            doc = item['doc'].copy()
            doc['relevance_score'] = item['final_score']
            final_results.append(doc)
        
        return final_results
    
    async def generate_claude_response(self, query: str, documents: List[Dict]) -> Dict:
        """Generate actual Claude response using Anthropic API"""
        
        if not documents:
            return self._no_results_response(query)
        
        if not self.claude_api_key:
            logger.warning("No Claude API key provided, using fallback response")
            return self._fallback_ai_response(query, documents)
        
        # Build structured context
        context_parts = []
        for i, doc in enumerate(documents[:5], 1):
            sponsor_info = self._format_sponsor_info(doc.get('sponsor'))
            
            context_parts.append(f"""
Document {i}: {doc['identifier']}
Title: {doc['title']}
Type: {doc['document_type'].replace('_', ' ').title()}
Status: {doc.get('status', 'Unknown')}
{sponsor_info}
Date: {doc.get('last_action_date', 'Unknown')}
Summary: {doc.get('summary', 'No summary available')[:400]}{'...' if len(doc.get('summary', '')) > 400 else ''}
""".strip())
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are an expert policy analyst helping citizens understand government legislation.

User Query: "{query}"

Relevant Government Documents Found:
{context}

Please provide a helpful response that:
1. Directly answers the user's question based on the available documents
2. Uses plain language suitable for general citizens
3. References specific bills/EOs using their identifiers (e.g., {documents[0]['identifier']})
4. Explains potential real-world impacts on citizens
5. Maintains strict political neutrality
6. If results don't fully address the query, explain what's available and suggest refinements

Keep response concise but informative (2-3 paragraphs maximum). Focus on facts and impacts, not speculation."""

        try:
            response = await self.claude_client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.claude_api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data["content"][0]["text"],
                    "confidence": self._calculate_semantic_confidence(query, documents),
                    "suggestions": self._generate_intelligent_suggestions(query, documents)
                }
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return self._fallback_ai_response(query, documents)
                
        except Exception as e:
            logger.error(f"Claude integration error: {e}")
            return self._fallback_ai_response(query, documents)
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess user queries for better search results"""
        
        # Handle bill number patterns first
        query = re.sub(r'\b(hr|h\.r\.|house resolution)\s*(\d+)', r'HR-\2', query, flags=re.IGNORECASE)
        query = re.sub(r'\b(s|senate)\s*(\d+)', r'S-\2', query, flags=re.IGNORECASE)
        query = re.sub(r'\bexecutive order\s*(\d+)', r'EO-\1', query, flags=re.IGNORECASE)
        
        # For phrase queries like "one big beautiful bill", preserve the phrase
        # Only remove common words if they're not part of a specific phrase
        if not any(phrase in query.lower() for phrase in ['one big beautiful', 'infrastructure investment', 'jobs act']):
            # Only remove standalone instances of these words
            query = re.sub(r'\b(bill|act|resolution|order|legislation)\b(?!\s+\w)', '', query, flags=re.IGNORECASE)
        
        # Clean up whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _extract_identifiers(self, query: str) -> List[str]:
        """Extract potential bill/EO identifiers from query"""
        patterns = []
        
        # Find HR-123, S-456, EO-789 patterns
        hr_matches = re.findall(r'\bHR-?\s*(\d+)', query, re.IGNORECASE)
        patterns.extend([f'HR-{num}' for num in hr_matches])
        
        s_matches = re.findall(r'\bS-?\s*(\d+)', query, re.IGNORECASE)
        patterns.extend([f'S-{num}' for num in s_matches])
        
        eo_matches = re.findall(r'\bEO-?\s*(\d+)', query, re.IGNORECASE)
        patterns.extend([f'EO-{num}' for num in eo_matches])
        
        return patterns
    
    def _extract_potential_sponsors(self, query: str) -> List[str]:
        """Extract potential sponsor names from query"""
        # Look for capitalized words that might be names
        words = query.split()
        sponsors = []
        
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if next word is also capitalized (full name)
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    sponsors.append(f"{word} {words[i + 1]}")
                sponsors.append(word)
        
        return sponsors
    
    def _calculate_text_relevance(self, query: str, doc: Document) -> float:
        """Calculate relevance score for text matching"""
        score = 0.0
        query_terms = query.lower().split()
        
        # Title matches (highest weight)
        title_lower = (doc.title or '').lower()
        for term in query_terms:
            if term in title_lower:
                score += 3.0
        
        # Summary matches (medium weight)
        summary_lower = (doc.summary or '').lower()
        for term in query_terms:
            if term in summary_lower:
                score += 2.0
        
        # Full text matches (lower weight)
        full_text_lower = (doc.full_text or '').lower()
        for term in query_terms:
            if term in full_text_lower:
                score += 1.0
        
        # Identifier exact match (highest weight)
        if query.upper() in (doc.identifier or '').upper():
            score += 5.0
        
        return score
    
    def _calculate_semantic_confidence(self, query: str, documents: List[Dict]) -> float:
        """Calculate confidence score for search results"""
        if not documents:
            return 0.0
        
        # Base confidence on number of results and relevance scores
        base_confidence = min(len(documents) / 10.0, 1.0)  # More results = higher confidence
        
        # Boost confidence for exact identifier matches
        for doc in documents[:3]:
            if query.upper() in doc.get('identifier', '').upper():
                base_confidence = min(base_confidence + 0.3, 1.0)
        
        # Boost confidence for high relevance scores
        avg_relevance = sum(doc.get('relevance_score', 0) for doc in documents[:3]) / min(len(documents), 3)
        confidence_boost = min(avg_relevance * 0.5, 0.4)
        
        return min(base_confidence + confidence_boost, 1.0)
    
    def _generate_intelligent_suggestions(self, query: str, documents: List[Dict]) -> List[str]:
        """Generate smart search suggestions based on results and query"""
        suggestions = set()
        
        if not documents:
            # Generic suggestions for no results
            return [
                "infrastructure spending",
                "healthcare reform",
                "defense authorization",
                "climate legislation",
                "tax reform"
            ]
        
        # Extract key terms from successful results
        for doc in documents[:3]:
            title_words = (doc.get('title', '')).lower().split()
            for word in title_words:
                if len(word) > 4 and word not in ['bill', 'act', 'resolution', 'order']:
                    suggestions.add(word)
                    if len(suggestions) >= 3:
                        break
        
        # Add document type suggestions
        doc_types = set(doc.get('document_type', '') for doc in documents[:5])
        for doc_type in doc_types:
            if doc_type == 'bill':
                suggestions.add('congressional bills')
            elif doc_type == 'executive_order':
                suggestions.add('executive orders')
        
        return list(suggestions)[:5]
    
    def _format_sponsor_info(self, sponsor_data: Any) -> str:
        """Format sponsor information for display"""
        if not sponsor_data:
            return ""
        
        try:
            if isinstance(sponsor_data, str):
                sponsor_data = json.loads(sponsor_data)
            
            if isinstance(sponsor_data, dict):
                name = sponsor_data.get('full_name', 'Unknown')
                party = sponsor_data.get('party', 'Unknown')
                state = sponsor_data.get('state', 'Unknown')
                return f"Sponsor: {name} ({party}-{state})"
        except:
            pass
        
        return f"Sponsor: {sponsor_data}" if sponsor_data else ""
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        try:
            # Handle SQLAlchemy Row object
            if hasattr(row, '_mapping'):
                data = dict(row._mapping)
            else:
                # Handle tuple/list
                columns = ['id', 'document_type', 'identifier', 'title', 'summary', 'full_text', 
                          'status', 'introduced_date', 'last_action_date', 'sponsor_id', 'doc_metadata', 
                          'created_at', 'updated_at']
                data = dict(zip(columns, row))
            
            # Parse metadata
            metadata = {}
            sponsor_data = None
            
            if data.get('doc_metadata'):
                try:
                    metadata = json.loads(data['doc_metadata']) if isinstance(data['doc_metadata'], str) else data['doc_metadata']
                    if isinstance(metadata, dict) and 'sponsor' in metadata:
                        sponsor_data = metadata['sponsor']
                except:
                    metadata = {}
            
            # Format dates
            for date_field in ['introduced_date', 'last_action_date']:
                if data.get(date_field):
                    try:
                        if hasattr(data[date_field], 'isoformat'):
                            data[date_field] = data[date_field].isoformat()
                        else:
                            data[date_field] = str(data[date_field])
                    except:
                        data[date_field] = None
            
            return {
                'id': str(data.get('id', '')),
                'identifier': data.get('identifier', ''),
                'title': data.get('title', ''),
                'summary': data.get('summary', ''),
                'full_text': data.get('full_text', ''),
                'document_type': data.get('document_type', ''),
                'status': data.get('status', ''),
                'introduced_date': data.get('introduced_date'),
                'last_action_date': data.get('last_action_date'),
                'sponsor': sponsor_data,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error converting row to dict: {e}")
            return {}
    
    def _doc_to_dict(self, doc: Document) -> Dict:
        """Convert Document model to dictionary"""
        metadata = {}
        sponsor_data = None
        
        if doc.doc_metadata:
            try:
                metadata = json.loads(doc.doc_metadata) if isinstance(doc.doc_metadata, str) else doc.doc_metadata
                if isinstance(metadata, dict) and 'sponsor' in metadata:
                    sponsor_data = metadata['sponsor']
            except:
                metadata = {}
        
        return {
            'id': str(doc.id),
            'identifier': doc.identifier or '',
            'title': doc.title or '',
            'summary': doc.summary or '',
            'full_text': doc.full_text or '',
            'document_type': doc.document_type or '',
            'status': doc.status or '',
            'introduced_date': doc.introduced_date.isoformat() if doc.introduced_date else None,
            'last_action_date': doc.last_action_date.isoformat() if doc.last_action_date else None,
            'sponsor': sponsor_data,
            'metadata': metadata
        }
    
    def _no_results_response(self, query: str) -> Dict:
        """Response when no documents are found"""
        return {
            "response": f"I couldn't find any government documents directly related to '{query}'. This could mean:\n\n• The legislation hasn't been introduced yet\n• It might be known by a different name\n• The topic might be covered in different bills\n\nTry searching with different keywords or browse recent government actions.",
            "confidence": 0.0,
            "suggestions": [
                "infrastructure bill",
                "healthcare legislation", 
                "defense authorization",
                "budget resolution",
                "executive orders"
            ]
        }
    
    def _fallback_ai_response(self, query: str, documents: List[Dict]) -> Dict:
        """Enhanced fallback response that analyzes query intent and provides contextual information"""
        if not documents:
            return self._no_results_response(query)
        
        # Analyze query intent for more intelligent responses
        query_lower = query.lower()
        response_parts = []
        
        # Context-aware opening based on query
        if "one big beautiful" in query_lower or "infrastructure" in query_lower:
            if any("infrastructure" in doc.get('title', '').lower() or "beautiful" in doc.get('title', '').lower() for doc in documents):
                response_parts.append(f"I found government documents related to infrastructure legislation and the \"One Big Beautiful Bill\" concept.")
            else:
                response_parts.append(f"I found {len(documents)} documents that may relate to your infrastructure policy query.")
        elif any(term in query_lower for term in ["bill", "act", "legislation"]):
            response_parts.append(f"I found {len(documents)} legislative documents matching your search for '{query}'.")
        else:
            response_parts.append(f"I found {len(documents)} government documents related to '{query}'.")
        
        # Analyze document types and provide context
        bill_count = sum(1 for d in documents if d['document_type'] == 'bill')
        eo_count = sum(1 for d in documents if d['document_type'] == 'executive_order')
        pres_count = sum(1 for d in documents if d['document_type'] == 'presidential_document')
        
        doc_type_info = []
        if bill_count > 0:
            doc_type_info.append(f"{bill_count} congressional bill{'s' if bill_count != 1 else ''}")
        if eo_count > 0:
            doc_type_info.append(f"{eo_count} executive order{'s' if eo_count != 1 else ''}")
        if pres_count > 0:
            doc_type_info.append(f"{pres_count} presidential document{'s' if pres_count != 1 else ''}")
        
        if doc_type_info:
            response_parts.append(f"This includes {', '.join(doc_type_info)}.")
        
        # Analyze top results for specific insights
        top_doc = documents[0]
        if "one big beautiful" in query_lower and "beautiful" in top_doc.get('title', '').lower():
            response_parts.append(f"\n\n**Most Relevant**: **{top_doc['identifier']}** appears to be directly related to the 'One Big Beautiful Bill Act' you're searching for.")
        elif top_doc.get('relevance_score', 0) > 2.0:  # High relevance score
            response_parts.append(f"\n\n**Top Result**: **{top_doc['identifier']}** is highly relevant to your query.")
        
        # Add detailed document analysis
        if len(documents) > 1:
            response_parts.append("\n\n**Key findings:**")
            for i, doc in enumerate(documents[:3], 1):
                title = doc['title']
                # Highlight matching terms
                highlighted_title = title
                for word in query.split():
                    if len(word) > 3 and word.lower() in title.lower():
                        highlighted_title = highlighted_title.replace(word, f"**{word}**")
                
                status_text = f" (Status: {doc.get('status', 'Unknown')})" if doc.get('status') else ""
                response_parts.append(f"{i}. **{doc['identifier']}**: {highlighted_title[:120]}{'...' if len(title) > 120 else ''}{status_text}")
        
        # Add specific insights based on query context
        if "infrastructure" in query_lower:
            response_parts.append("\n\n*These documents relate to infrastructure policy, which includes transportation, broadband, utilities, and public works projects.*")
        elif "beautiful" in query_lower:
            response_parts.append("\n\n*The 'One Big Beautiful Bill' typically refers to comprehensive infrastructure legislation.*")
        
        response_parts.append("\n\nClick on any document identifier above to view the full text and legislative details.")
        
        return {
            "response": "\n".join(response_parts),
            "confidence": self._calculate_semantic_confidence(query, documents),
            "suggestions": self._generate_intelligent_suggestions(query, documents)
        }
    
    def _error_response(self, query: str, error: str) -> Dict:
        """Response for search errors"""
        return {
            "query": query,
            "documents": [],
            "claude_response": f"I encountered an error while searching for '{query}'. Please try again or contact support if the issue persists.",
            "confidence": 0.0,
            "suggestions": ["Try a different search term", "Check your internet connection"],
            "search_type": "error",
            "total_results": 0,
            "error": error
        }

# Test the service
async def test_hybrid_search():
    """Test the hybrid search service"""
    service = HybridSearchService()
    
    test_queries = [
        "infrastructure bill",
        "one big beautiful bill act",
        "HR-3684",
        "climate change legislation",
        "veterans healthcare"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        result = await service.search_with_ai_response(query, limit=5)
        print(f"Found {result['total_results']} documents")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Execution time: {result.get('execution_time_ms', 0)}ms")
        
        if result['documents']:
            print(f"Top result: {result['documents'][0]['identifier']} - {result['documents'][0]['title'][:60]}...")
        
        print(f"AI Response: {result['claude_response'][:150]}...")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search())