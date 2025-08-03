#!/usr/bin/env python3
"""
Enhanced search implementation following technical_search_implementation_guide.md
Implements improved keyword search as a foundation for future semantic search.
"""
import asyncio
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, or_, and_, func, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from minimal_init import Document

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class EnhancedSearchService:
    """
    Enhanced search service implementing better keyword matching.
    Future foundation for Elasticsearch/ELSER semantic search integration.
    """
    
    def __init__(self):
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
    
    async def enhanced_search(self, 
                            query: str, 
                            limit: int = 20, 
                            offset: int = 0,
                            document_type: Optional[str] = None) -> Tuple[List[Document], int]:
        """
        Enhanced search with better keyword matching and ranking.
        
        Following technical_search_implementation_guide.md recommendations for
        hybrid search preparation.
        """
        
        # Process query for better matching
        processed_query = self._process_query(query)
        search_terms = self._extract_search_terms(query)
        
        async with AsyncSessionLocal() as db:
            # Build the base query
            base_stmt = select(Document)
            
            if document_type:
                base_stmt = base_stmt.where(Document.document_type == document_type)
            
            # Multi-tier search strategy
            results = []
            
            # Tier 1: Exact phrase matches (highest priority)
            if len(query.strip()) > 3:
                exact_matches = await self._exact_phrase_search(db, base_stmt, query, limit)
                results.extend(exact_matches)
            
            # Tier 2: All terms present (high priority)
            if len(results) < limit and len(search_terms) > 1:
                all_terms_matches = await self._all_terms_search(db, base_stmt, search_terms, limit - len(results))
                # Remove duplicates
                existing_ids = {doc.id for doc in results}
                all_terms_matches = [doc for doc in all_terms_matches if doc.id not in existing_ids]
                results.extend(all_terms_matches)
            
            # Tier 3: Any term matches (standard priority)
            if len(results) < limit:
                any_term_matches = await self._any_term_search(db, base_stmt, search_terms, limit - len(results))
                # Remove duplicates
                existing_ids = {doc.id for doc in results}
                any_term_matches = [doc for doc in any_term_matches if doc.id not in existing_ids]
                results.extend(any_term_matches)
            
            # Tier 4: Partial/fuzzy matches (lower priority)
            if len(results) < limit:
                partial_matches = await self._partial_match_search(db, base_stmt, search_terms, limit - len(results))
                # Remove duplicates
                existing_ids = {doc.id for doc in results}
                partial_matches = [doc for doc in partial_matches if doc.id not in existing_ids]
                results.extend(partial_matches)
            
            # Get total count for pagination
            count_stmt = select(func.count(Document.id))
            if document_type:
                count_stmt = count_stmt.where(Document.document_type == document_type)
            
            # Use same search logic for count
            total_conditions = []
            for term in search_terms:
                term_condition = or_(
                    Document.title.ilike(f"%{term}%"),
                    Document.summary.ilike(f"%{term}%"),
                    Document.identifier.ilike(f"%{term}%")
                )
                total_conditions.append(term_condition)
            
            if total_conditions:
                count_stmt = count_stmt.where(or_(*total_conditions))
            
            count_result = await db.execute(count_stmt)
            total_count = count_result.scalar() or 0
            
            # Apply pagination
            paginated_results = results[offset:offset + limit]
            
            return paginated_results, total_count
    
    def _process_query(self, query: str) -> str:
        """Clean and normalize the search query"""
        # Remove extra whitespace and normalize
        query = re.sub(r'\s+', ' ', query.strip().lower())
        
        # Handle common synonyms and government terms
        query = query.replace('eo ', 'executive order ')
        query = query.replace('hr ', 'house resolution ')
        query = query.replace('sr ', 'senate resolution ')
        query = query.replace('va ', 'veterans affairs ')
        
        return query
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from query"""
        # Split on whitespace and punctuation
        terms = re.findall(r'\b\w+\b', query.lower())
        
        # Remove stopwords and short terms
        meaningful_terms = [
            term for term in terms 
            if len(term) >= 2 and term not in self.stopwords
        ]
        
        return meaningful_terms
    
    async def _exact_phrase_search(self, db: AsyncSession, base_stmt, query: str, limit: int) -> List[Document]:
        """Search for exact phrase matches"""
        clean_query = query.strip()
        if len(clean_query) < 3:
            return []
        
        stmt = base_stmt.where(
            or_(
                Document.title.ilike(f"%{clean_query}%"),
                Document.summary.ilike(f"%{clean_query}%")
            )
        ).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _all_terms_search(self, db: AsyncSession, base_stmt, terms: List[str], limit: int) -> List[Document]:
        """Search requiring all terms to be present"""
        if len(terms) <= 1:
            return []
        
        conditions = []
        for term in terms:
            term_condition = or_(
                Document.title.ilike(f"%{term}%"),
                Document.summary.ilike(f"%{term}%"),
                Document.identifier.ilike(f"%{term}%")
            )
            conditions.append(term_condition)
        
        stmt = base_stmt.where(and_(*conditions)).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _any_term_search(self, db: AsyncSession, base_stmt, terms: List[str], limit: int) -> List[Document]:
        """Search for any term matches"""
        if not terms:
            return []
        
        conditions = []
        for term in terms:
            term_condition = or_(
                Document.title.ilike(f"%{term}%"),
                Document.summary.ilike(f"%{term}%"),
                Document.identifier.ilike(f"%{term}%")
            )
            conditions.append(term_condition)
        
        stmt = base_stmt.where(or_(*conditions)).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _partial_match_search(self, db: AsyncSession, base_stmt, terms: List[str], limit: int) -> List[Document]:
        """Search for partial/fuzzy matches"""
        if not terms:
            return []
        
        # For SQLite, we'll use simple partial matching
        # In production, this would use Elasticsearch fuzzy matching
        conditions = []
        for term in terms:
            if len(term) >= 4:  # Only fuzzy match longer terms
                # Simple character-based partial matching
                partial_term = f"%{term[:-1]}%"  # Remove last character for fuzzy effect
                term_condition = or_(
                    Document.title.ilike(partial_term),
                    Document.summary.ilike(partial_term)
                )
                conditions.append(term_condition)
        
        if not conditions:
            return []
        
        stmt = base_stmt.where(or_(*conditions)).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

# Test the enhanced search
async def test_enhanced_search():
    """Test the enhanced search functionality"""
    search_service = EnhancedSearchService()
    
    test_queries = [
        "veterans healthcare",
        "tax policy",
        "immigration border",
        "climate environment",
        "infrastructure transportation"
    ]
    
    print("🔍 Testing Enhanced Search Service")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results, total = await search_service.enhanced_search(query, limit=3)
        print(f"Results: {len(results)} of {total} total")
        
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.identifier}: {doc.title[:60]}...")
            if doc.summary:
                print(f"     Summary: {doc.summary[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_enhanced_search())