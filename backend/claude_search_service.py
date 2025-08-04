#!/usr/bin/env python3
"""
Enhanced search service with Claude-generated responses
Provides conversational search results with bill links and explanations
"""
import asyncio
import json
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document
import httpx

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class ClaudeSearchService:
    def __init__(self):
        self.anthropic_api_key = "your-api-key-here"  # Replace with actual key
        
    async def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Enhanced search with multiple strategies"""
        async with AsyncSessionLocal() as db:
            results = []
            
            # 1. Exact phrase search
            exact_results = await self._exact_phrase_search(db, query, limit//2)
            results.extend(exact_results)
            
            # 2. Semantic/fuzzy search
            remaining_limit = limit - len(results)
            if remaining_limit > 0:
                fuzzy_results = await self._fuzzy_search(db, query, remaining_limit)
                # Add only new results
                existing_ids = {r['id'] for r in results}
                for result in fuzzy_results:
                    if result['id'] not in existing_ids:
                        results.append(result)
                        if len(results) >= limit:
                            break
            
            return results
    
    async def _exact_phrase_search(self, db: AsyncSession, query: str, limit: int) -> List[Dict]:
        """Search for exact phrases in documents"""
        # Try FTS search first, fall back to regular search
        try:
            # Simple LIKE search since FTS may not be set up
            sql = """
            SELECT 
                id, identifier, title, summary, full_text, document_type, 
                status, introduced_date, last_action_date, sponsor, doc_metadata
            FROM documents 
            WHERE title LIKE ? OR summary LIKE ? OR full_text LIKE ?
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    WHEN summary LIKE ? THEN 2
                    ELSE 3
                END,
                last_action_date DESC
            LIMIT ?
            """
            
            pattern = f"%{query}%"
            result = await db.execute(text(sql), (pattern, pattern, pattern, pattern, pattern, limit))
            rows = result.fetchall()
            
            documents = []
            for row in rows:
                # Convert dates to strings if they exist
                intro_date = row[7].isoformat() if row[7] else None
                action_date = row[8].isoformat() if row[8] else None
                
                # Parse JSON fields safely
                sponsor_data = None
                if row[9]:
                    try:
                        sponsor_data = json.loads(row[9]) if isinstance(row[9], str) else row[9]
                    except:
                        sponsor_data = None
                
                metadata = {}
                if row[10]:
                    try:
                        metadata = json.loads(row[10]) if isinstance(row[10], str) else row[10]
                    except:
                        metadata = {}
                
                doc_dict = {
                    'id': str(row[0]),
                    'identifier': str(row[1]) if row[1] else '',
                    'title': str(row[2]) if row[2] else '',
                    'summary': str(row[3]) if row[3] else '',
                    'full_text': str(row[4]) if row[4] else '',
                    'document_type': str(row[5]) if row[5] else '',
                    'status': str(row[6]) if row[6] else '',
                    'introduced_date': intro_date,
                    'last_action_date': action_date,
                    'sponsor': sponsor_data,
                    'metadata': metadata
                }
                documents.append(doc_dict)
            
            return documents
            
        except Exception as e:
            print(f"Exact phrase search error: {e}")
            return await self._fallback_search(db, query, limit)
    
    async def _fuzzy_search(self, db: AsyncSession, query: str, limit: int) -> List[Dict]:
        """Fuzzy search using LIKE patterns"""
        search_terms = query.lower().split()
        
        # Build flexible search conditions
        conditions = []
        params = []
        
        for term in search_terms:
            if len(term) > 2:  # Skip very short terms
                conditions.append("(title LIKE ? OR summary LIKE ? OR full_text LIKE ?)")
                params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
        
        if not conditions:
            return []
        
        sql = f"""
        SELECT 
            id, identifier, title, summary, full_text, document_type, 
            status, introduced_date, last_action_date, sponsor, doc_metadata
        FROM documents 
        WHERE {' OR '.join(conditions)}
        ORDER BY 
            CASE 
                WHEN title LIKE ? THEN 1
                WHEN summary LIKE ? THEN 2  
                ELSE 3
            END,
            last_action_date DESC
        LIMIT ?
        """
        
        # Add primary search term for ranking
        primary_term = f"%{search_terms[0]}%"
        params.extend([primary_term, primary_term, limit])
        
        try:
            result = await db.execute(text(sql), params)
            rows = result.fetchall()
            
            documents = []
            for row in rows:
                # Convert dates to strings if they exist
                intro_date = row[7].isoformat() if row[7] else None
                action_date = row[8].isoformat() if row[8] else None
                
                # Parse JSON fields safely
                sponsor_data = None
                if row[9]:
                    try:
                        sponsor_data = json.loads(row[9]) if isinstance(row[9], str) else row[9]
                    except:
                        sponsor_data = None
                
                metadata = {}
                if row[10]:
                    try:
                        metadata = json.loads(row[10]) if isinstance(row[10], str) else row[10]
                    except:
                        metadata = {}
                
                doc_dict = {
                    'id': str(row[0]),
                    'identifier': str(row[1]) if row[1] else '',
                    'title': str(row[2]) if row[2] else '',
                    'summary': str(row[3]) if row[3] else '',
                    'full_text': str(row[4]) if row[4] else '',
                    'document_type': str(row[5]) if row[5] else '',
                    'status': str(row[6]) if row[6] else '',
                    'introduced_date': intro_date,
                    'last_action_date': action_date,
                    'sponsor': sponsor_data,
                    'metadata': metadata
                }
                documents.append(doc_dict)
            
            return documents
            
        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return []
    
    async def _fallback_search(self, db: AsyncSession, query: str, limit: int) -> List[Dict]:
        """Simple fallback search"""
        sql = """
        SELECT 
            id, identifier, title, summary, full_text, document_type, 
            status, introduced_date, last_action_date, sponsor, doc_metadata
        FROM documents 
        WHERE title LIKE ? OR summary LIKE ?
        ORDER BY last_action_date DESC
        LIMIT ?
        """
        
        pattern = f"%{query}%"
        result = await db.execute(text(sql), (pattern, pattern, limit))
        rows = result.fetchall()
        
        documents = []
        for row in rows:
            # Convert dates to strings if they exist
            intro_date = row[7].isoformat() if row[7] else None
            action_date = row[8].isoformat() if row[8] else None
            
            # Parse JSON fields safely
            sponsor_data = None
            if row[9]:
                try:
                    sponsor_data = json.loads(row[9]) if isinstance(row[9], str) else row[9]
                except:
                    sponsor_data = None
            
            metadata = {}
            if row[10]:
                try:
                    metadata = json.loads(row[10]) if isinstance(row[10], str) else row[10]
                except:
                    metadata = {}
            
            doc_dict = {
                'id': str(row[0]),
                'identifier': str(row[1]) if row[1] else '',
                'title': str(row[2]) if row[2] else '',
                'summary': str(row[3]) if row[3] else '',
                'full_text': str(row[4]) if row[4] else '',
                'document_type': str(row[5]) if row[5] else '',
                'status': str(row[6]) if row[6] else '',
                'introduced_date': intro_date,
                'last_action_date': action_date,
                'sponsor': sponsor_data,
                'metadata': metadata
            }
            documents.append(doc_dict)
        
        return documents
    
    async def generate_claude_response(self, query: str, relevant_documents: List[Dict]) -> Dict:
        """Generate Claude response for search results"""
        if not relevant_documents:
            return {
                "response": f"I couldn't find any government documents directly related to '{query}'. This could mean:\n\n• The legislation hasn't been introduced yet\n• It might be known by a different name\n• The topic might be covered in different bills\n\nTry searching with different keywords or browse recent government actions.",
                "source_documents": [],
                "confidence": 0.0,
                "suggestions": [
                    "infrastructure bill",
                    "healthcare legislation", 
                    "defense authorization",
                    "budget resolution"
                ]
            }
        
        # Build context for Claude
        context_parts = []
        for i, doc in enumerate(relevant_documents[:5], 1):
            context_parts.append(f"""
            Document {i}: {doc['identifier']}
            Title: {doc['title']}
            Type: {doc['document_type'].replace('_', ' ').title()}
            Status: {doc.get('status', 'Unknown')}
            Summary: {doc.get('summary', 'No summary available')[:500]}
            """)
        
        context = "\n".join(context_parts)
        
        # Create prompt for Claude
        prompt = f"""You are an expert policy analyst helping citizens understand government actions. 

User Query: "{query}"

Relevant Government Documents:
{context}

Please provide a helpful response that:
1. Directly answers the user's question based on the available documents
2. Uses plain language suitable for general citizens
3. References specific bills/EOs using their identifiers (e.g., HR-1234, S-567, EO-14001)
4. Highlights key impacts on citizens
5. Maintains political neutrality
6. If the query seems to be looking for something specific but the results don't match well, suggest what the user might be looking for

Keep the response concise but informative (2-3 paragraphs maximum).
"""

        try:
            # For now, create a mock response since we don't have the actual Claude API key
            # In production, you would use the Anthropic API here
            response_text = self._generate_mock_response(query, relevant_documents)
            
            return {
                "response": response_text,
                "source_documents": relevant_documents,
                "confidence": self._calculate_confidence(query, relevant_documents),
                "suggestions": self._generate_suggestions(query, relevant_documents)
            }
            
        except Exception as e:
            print(f"Error generating Claude response: {e}")
            return {
                "response": f"I found {len(relevant_documents)} government documents related to '{query}'. Please see the results below for detailed information.",
                "source_documents": relevant_documents,
                "confidence": 0.5,
                "suggestions": []
            }
    
    def _generate_mock_response(self, query: str, documents: List[Dict]) -> str:
        """Generate a mock response (replace with actual Claude API call)"""
        if not documents:
            return f"I couldn't find any government documents directly related to '{query}'."
        
        # Analyze document types and topics
        bill_count = sum(1 for d in documents if d['document_type'] == 'bill')
        eo_count = sum(1 for d in documents if d['document_type'] == 'executive_order')
        
        response_parts = []
        
        # Opening
        if len(documents) == 1:
            doc = documents[0]
            response_parts.append(f"I found one relevant document: **{doc['identifier']}** - {doc['title']}.")
        else:
            response_parts.append(f"I found {len(documents)} government documents related to '{query}'.")
            if bill_count > 0:
                response_parts.append(f"This includes {bill_count} congressional bill{'s' if bill_count != 1 else ''}")
            if eo_count > 0:
                response_parts.append(f"{' and ' if bill_count > 0 else 'This includes '}{eo_count} executive order{'s' if eo_count != 1 else ''}.")
        
        # Highlight key documents
        key_docs = documents[:3]
        if len(key_docs) > 1:
            response_parts.append("\n\n**Key documents include:**")
            for doc in key_docs:
                status_text = f" (Status: {doc.get('status', 'Unknown')})" if doc.get('status') else ""
                response_parts.append(f"• **{doc['identifier']}**: {doc['title'][:100]}{'...' if len(doc['title']) > 100 else ''}{status_text}")
        
        # Add summary if available
        if documents[0].get('summary'):
            summary = documents[0]['summary'][:300]
            response_parts.append(f"\n\n{summary}{'...' if len(documents[0].get('summary', '')) > 300 else ''}")
        
        # Closing
        response_parts.append(f"\n\nClick on any document title below to view full details and official sources.")
        
        return "\n".join(response_parts)
    
    def _calculate_confidence(self, query: str, documents: List[Dict]) -> float:
        """Calculate confidence score based on search relevance"""
        if not documents:
            return 0.0
        
        query_terms = set(query.lower().split())
        total_score = 0
        
        for doc in documents[:5]:  # Only consider top 5 for confidence
            title_terms = set(doc.get('title', '').lower().split())
            summary_terms = set(doc.get('summary', '').lower().split())
            
            # Calculate term overlap
            title_overlap = len(query_terms.intersection(title_terms)) / len(query_terms) if query_terms else 0
            summary_overlap = len(query_terms.intersection(summary_terms)) / len(query_terms) if query_terms else 0
            
            doc_score = max(title_overlap, summary_overlap * 0.7)
            total_score += doc_score
        
        return min(total_score / len(documents[:5]), 1.0)
    
    def _generate_suggestions(self, query: str, documents: List[Dict]) -> List[str]:
        """Generate search suggestions based on results"""
        if not documents:
            return [
                "infrastructure bill",
                "healthcare legislation",
                "defense authorization",
                "budget resolution",
                "executive order"
            ]
        
        suggestions = set()
        
        # Extract common terms from successful results
        for doc in documents:
            title_words = doc.get('title', '').lower().split()
            for word in title_words:
                if len(word) > 4 and word not in ['bill', 'act', 'order', 'resolution']:
                    suggestions.add(word)
                    if len(suggestions) >= 5:
                        break
        
        return list(suggestions)[:5]

# Test the service
async def test_search_service():
    """Test the search service"""
    service = ClaudeSearchService()
    
    # Test queries
    test_queries = [
        "infrastructure bill",
        "one big beautiful bill act",
        "climate change",
        "healthcare",
        "defense authorization"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Search for documents
        documents = await service.search_documents(query, limit=5)
        print(f"Found {len(documents)} documents")
        
        # Generate Claude response
        response = await service.generate_claude_response(query, documents)
        print(f"Confidence: {response['confidence']:.2f}")
        print(f"Response preview: {response['response'][:200]}...")

if __name__ == "__main__":
    asyncio.run(test_search_service())