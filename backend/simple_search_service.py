#!/usr/bin/env python3
"""
Simple search service that works with our current database setup
"""
import asyncio
import json
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, or_, and_, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class SimpleSearchService:
    def __init__(self):
        pass
        
    async def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple document search"""
        async with AsyncSessionLocal() as db:
            try:
                # Use SQLAlchemy ORM for simpler parameter binding
                search_terms = query.lower().split()
                
                # Build search conditions
                conditions = []
                for term in search_terms:
                    if len(term) > 2:
                        term_condition = or_(
                            Document.title.ilike(f"%{term}%"),
                            Document.summary.ilike(f"%{term}%"),
                            Document.full_text.ilike(f"%{term}%")
                        )
                        conditions.append(term_condition)
                
                if not conditions:
                    # If no valid search terms, return recent documents
                    stmt = select(Document).order_by(Document.last_action_date.desc()).limit(limit)
                else:
                    # Combine conditions with OR
                    final_condition = or_(*conditions)
                    stmt = select(Document).where(final_condition).order_by(Document.last_action_date.desc()).limit(limit)
                
                result = await db.execute(stmt)
                documents = result.scalars().all()
                
                # Convert to dictionaries
                doc_list = []
                for doc in documents:
                    # Parse metadata (sponsor data might be stored here)
                    metadata = {}
                    sponsor_data = None
                    if doc.doc_metadata:
                        try:
                            metadata = json.loads(doc.doc_metadata) if isinstance(doc.doc_metadata, str) else doc.doc_metadata
                            # Check if sponsor data is in metadata
                            if isinstance(metadata, dict) and 'sponsor' in metadata:
                                sponsor_data = metadata['sponsor']
                        except Exception as e:
                            print(f"Error parsing metadata: {e}")
                            metadata = {}
                    
                    doc_dict = {
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
                    doc_list.append(doc_dict)
                
                return doc_list
                
            except Exception as e:
                print(f"Search error: {e}")
                return []
    
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
        
        # Generate response based on found documents
        response_parts = []
        
        # Analyze document types and topics
        bill_count = sum(1 for d in relevant_documents if d['document_type'] == 'bill')
        eo_count = sum(1 for d in relevant_documents if d['document_type'] == 'executive_order')
        
        # Opening
        if len(relevant_documents) == 1:
            doc = relevant_documents[0]
            response_parts.append(f"I found one relevant document: **{doc['identifier']}** - {doc['title']}.")
        else:
            response_parts.append(f"I found {len(relevant_documents)} government documents related to '{query}'.")
            if bill_count > 0:
                response_parts.append(f"This includes {bill_count} congressional bill{'s' if bill_count != 1 else ''}")
            if eo_count > 0:
                response_parts.append(f"{' and ' if bill_count > 0 else 'This includes '}{eo_count} executive order{'s' if eo_count != 1 else ''}.")
        
        # Highlight key documents
        key_docs = relevant_documents[:3]
        if len(key_docs) > 1:
            response_parts.append("\n\n**Key documents include:**")
            for doc in key_docs:
                status_text = f" (Status: {doc.get('status', 'Unknown')})" if doc.get('status') else ""
                response_parts.append(f"• **{doc['identifier']}**: {doc['title'][:100]}{'...' if len(doc['title']) > 100 else ''}{status_text}")
        
        # Add summary if available
        if relevant_documents[0].get('summary'):
            summary = relevant_documents[0]['summary'][:300]
            response_parts.append(f"\n\n{summary}{'...' if len(relevant_documents[0].get('summary', '')) > 300 else ''}")
        
        # Closing
        response_parts.append(f"\n\nClick on any document title below to view full details and official sources.")
        
        # Calculate confidence
        confidence = self._calculate_confidence(query, relevant_documents)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(query, relevant_documents)
        
        return {
            "response": "\n".join(response_parts),
            "source_documents": relevant_documents,
            "confidence": confidence,
            "suggestions": suggestions
        }
    
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
    service = SimpleSearchService()
    
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
        documents = await service.search_documents(query, limit=3)
        print(f"Found {len(documents)} documents")
        
        if documents:
            print(f"Sample: {documents[0]['identifier']} - {documents[0]['title'][:60]}...")
        
        # Generate Claude response
        response = await service.generate_claude_response(query, documents)
        print(f"Confidence: {response['confidence']:.2f}")
        print(f"Response preview: {response['response'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_search_service())