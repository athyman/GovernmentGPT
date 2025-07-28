"""
Document endpoints for GovernmentGPT API.
Handles individual document retrieval and metadata.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_db
from app.schemas.document import DocumentResponse, DocumentSummary
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str = Path(..., description="Document ID or identifier"),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Get full document details by ID or identifier"""
    try:
        document_service = DocumentService(db)
        document = await document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {document_id}"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.get("/{document_id}/summary", response_model=DocumentSummary)
async def get_document_summary(
    document_id: str = Path(..., description="Document ID or identifier"),
    db: AsyncSession = Depends(get_db)
) -> DocumentSummary:
    """Get AI-generated summary of document"""
    try:
        document_service = DocumentService(db)
        summary = await document_service.get_document_summary(document_id)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {document_id}"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document summary error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List documents with pagination and filtering"""
    try:
        document_service = DocumentService(db)
        documents = await document_service.list_documents(
            skip=skip,
            limit=limit,
            document_type=document_type,
            status=status
        )
        
        return documents
        
    except Exception as e:
        logger.error(f"Document listing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )