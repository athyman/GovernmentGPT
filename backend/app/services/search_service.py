"""
Search service for GovernmentGPT.
Handles document search operations and AI summarization.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, or_, and_
from typing import List, Optional, Dict, Any
import time
import logging

from app.models.document import Document
from app.models.legislator import Legislator
from app.models.search import PopularSearches, SearchCache
from app.schemas.search import SearchRequest, SearchResponse, DocumentResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for handling document search operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search(self, search_request: SearchRequest) -> SearchResponse:
        """
        Perform document search based on request parameters.
        Currently implements PostgreSQL full-text search.
        TODO: Add semantic search and AI summarization.
        """
        start_time = time.time()
        
        try:
            # Build base query
            query = select(Document).join(Legislator, Document.sponsor_id == Legislator.id, isouter=True)
            
            # Apply text search
            if search_request.query:
                search_vector = func.to_tsvector('english', 
                    Document.title + ' ' + 
                    func.coalesce(Document.summary, '') + ' ' + 
                    Document.full_text
                )
                search_query = func.plainto_tsquery('english', search_request.query)
                query = query.where(search_vector.match(search_query))
            
            # Apply filters
            if search_request.filters:
                if search_request.filters.document_type:
                    query = query.where(Document.document_type == search_request.filters.document_type.value)
                
                if search_request.filters.status:
                    query = query.where(Document.status == search_request.filters.status)
                
                if search_request.filters.date_from:
                    query = query.where(Document.introduced_date >= search_request.filters.date_from.date())
                
                if search_request.filters.date_to:
                    query = query.where(Document.introduced_date <= search_request.filters.date_to.date())
            
            # Add ordering and pagination
            query = query.order_by(Document.last_action_date.desc().nullslast())
            query = query.offset(search_request.offset).limit(search_request.limit)
            
            # Execute query
            result = await self.db.execute(query)
            documents = result.scalars().all()
            
            # Convert to response format
            document_results = []
            for doc in documents:
                document_results.append(DocumentResult(
                    id=str(doc.id),
                    identifier=doc.identifier,
                    title=doc.title,
                    summary=doc.summary,
                    document_type=doc.document_type,
                    status=doc.status,
                    introduced_date=doc.introduced_date,
                    last_action_date=doc.last_action_date,
                    sponsor_name=doc.sponsor.full_name if doc.sponsor else None,
                    sponsor_party=doc.sponsor.party if doc.sponsor else None,
                    sponsor_state=doc.sponsor.state if doc.sponsor else None,
                    relevance_score=1.0  # TODO: Calculate actual relevance
                ))
            
            response_time = int((time.time() - start_time) * 1000)
            
            return SearchResponse(
                query=search_request.query,
                search_type=search_request.search_type,
                total_results=len(document_results),  # TODO: Get actual count
                returned_results=len(document_results),
                response_time_ms=response_time,
                documents=document_results,
                filters_applied=search_request.filters
            )
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
    
    async def get_recent_documents(self, limit: int, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recently introduced documents"""
        try:
            query = select(Document).join(Legislator, Document.sponsor_id == Legislator.id, isouter=True)
            
            if document_type:
                query = query.where(Document.document_type == document_type)
            
            query = query.order_by(Document.introduced_date.desc().nullslast()).limit(limit)
            
            result = await self.db.execute(query)
            documents = result.scalars().all()
            
            return [
                {
                    "id": str(doc.id),
                    "identifier": doc.identifier,
                    "title": doc.title,
                    "summary": doc.summary,
                    "document_type": doc.document_type,
                    "status": doc.status,
                    "introduced_date": doc.introduced_date.isoformat() if doc.introduced_date else None,
                    "sponsor": {
                        "name": doc.sponsor.full_name,
                        "party": doc.sponsor.party,
                        "state": doc.sponsor.state
                    } if doc.sponsor else None
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Recent documents error: {str(e)}")
            raise
    
    async def get_search_suggestions(self, query: str, limit: int) -> List[str]:
        """Get search suggestions based on popular searches"""
        try:
            # Simple implementation - search popular searches
            stmt = select(PopularSearches.query).where(
                PopularSearches.normalized_query.ilike(f"%{query.lower()}%")
            ).order_by(PopularSearches.search_count.desc()).limit(limit)
            
            result = await self.db.execute(stmt)
            suggestions = result.scalars().all()
            
            return list(suggestions) if suggestions else []
            
        except Exception as e:
            logger.error(f"Search suggestions error: {str(e)}")
            return []