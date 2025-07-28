"""
Search endpoints for GovernmentGPT API.
Handles document search and AI-powered summarization.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SearchResponse)
async def search_documents(
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:
    """
    Search government documents with AI-powered summarization.
    
    Supports:
    - Keyword search
    - Semantic search
    - Hybrid search (combines both)
    - Conversational AI responses
    """
    try:
        search_service = SearchService(db)
        result = await search_service.search(search_request)
        return result
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/recent")
async def get_recent_documents(
    limit: int = Query(10, ge=1, le=50),
    document_type: Optional[str] = Query(None, regex="^(bill|executive_order)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get recently introduced documents"""
    try:
        search_service = SearchService(db)
        documents = await search_service.get_recent_documents(limit, document_type)
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"Recent documents error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent documents: {str(e)}"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Get search query suggestions"""
    try:
        search_service = SearchService(db)
        suggestions = await search_service.get_search_suggestions(query, limit)
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Search suggestions error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get suggestions: {str(e)}"
        )