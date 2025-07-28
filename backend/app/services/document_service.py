"""
Document service for GovernmentGPT.
Handles individual document operations and management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict, Any, List
import logging

from app.models.document import Document
from app.models.legislator import Legislator
from app.schemas.document import DocumentResponse, DocumentSummary, LegislatorInfo

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling individual document operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get full document details by ID or identifier"""
        try:
            # Try to get by UUID first, then by identifier
            query = select(Document).join(Legislator, Document.sponsor_id == Legislator.id, isouter=True)
            
            try:
                # Try UUID first
                import uuid
                uuid_obj = uuid.UUID(document_id)
                query = query.where(Document.id == uuid_obj)
            except ValueError:
                # Not a UUID, try identifier
                query = query.where(Document.identifier == document_id)
            
            result = await self.db.execute(query)
            document = result.scalar_one_or_none()
            
            if not document:
                return None
            
            # Convert to response schema
            sponsor_info = None
            if document.sponsor:
                sponsor_info = LegislatorInfo(
                    id=str(document.sponsor.id),
                    bioguide_id=document.sponsor.bioguide_id,
                    full_name=document.sponsor.full_name,
                    party=document.sponsor.party,
                    state=document.sponsor.state,
                    district=document.sponsor.district,
                    chamber=document.sponsor.chamber
                )
            
            return DocumentResponse(
                id=str(document.id),
                identifier=document.identifier,
                title=document.title,
                summary=document.summary,
                full_text=document.full_text,
                document_type=document.document_type,
                status=document.status,
                introduced_date=document.introduced_date,
                last_action_date=document.last_action_date,
                sponsor=sponsor_info,
                metadata=document.metadata or {},
                created_at=document.created_at,
                updated_at=document.updated_at
            )
            
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            raise
    
    async def get_document_summary(self, document_id: str) -> Optional[DocumentSummary]:
        """Get AI-generated summary of document"""
        try:
            # Get basic document info
            query = select(Document).join(Legislator, Document.sponsor_id == Legislator.id, isouter=True)
            
            try:
                import uuid
                uuid_obj = uuid.UUID(document_id)
                query = query.where(Document.id == uuid_obj)
            except ValueError:
                query = query.where(Document.identifier == document_id)
            
            result = await self.db.execute(query)
            document = result.scalar_one_or_none()
            
            if not document:
                return None
            
            # Convert to summary schema
            sponsor_info = None
            if document.sponsor:
                sponsor_info = LegislatorInfo(
                    id=str(document.sponsor.id),
                    bioguide_id=document.sponsor.bioguide_id,
                    full_name=document.sponsor.full_name,
                    party=document.sponsor.party,
                    state=document.sponsor.state,
                    district=document.sponsor.district,
                    chamber=document.sponsor.chamber
                )
            
            return DocumentSummary(
                id=str(document.id),
                identifier=document.identifier,
                title=document.title,
                summary=document.summary,
                document_type=document.document_type,
                status=document.status,
                introduced_date=document.introduced_date,
                last_action_date=document.last_action_date,
                sponsor=sponsor_info
            )
            
        except Exception as e:
            logger.error(f"Document summary error: {str(e)}")
            raise
    
    async def list_documents(
        self, 
        skip: int = 0, 
        limit: int = 20,
        document_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List documents with pagination and filtering"""
        try:
            # Build base query
            query = select(Document).join(Legislator, Document.sponsor_id == Legislator.id, isouter=True)
            count_query = select(func.count(Document.id))
            
            # Apply filters
            if document_type:
                query = query.where(Document.document_type == document_type)
                count_query = count_query.where(Document.document_type == document_type)
            
            if status:
                query = query.where(Document.status == status)
                count_query = count_query.where(Document.status == status)
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total_count = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(Document.introduced_date.desc().nullslast())
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            documents = result.scalars().all()
            
            # Convert to summary format
            document_summaries = []
            for doc in documents:
                sponsor_info = None
                if doc.sponsor:
                    sponsor_info = LegislatorInfo(
                        id=str(doc.sponsor.id),
                        bioguide_id=doc.sponsor.bioguide_id,
                        full_name=doc.sponsor.full_name,
                        party=doc.sponsor.party,
                        state=doc.sponsor.state,
                        district=doc.sponsor.district,
                        chamber=doc.sponsor.chamber
                    )
                
                document_summaries.append(DocumentSummary(
                    id=str(doc.id),
                    identifier=doc.identifier,
                    title=doc.title,
                    summary=doc.summary,
                    document_type=doc.document_type,
                    status=doc.status,
                    introduced_date=doc.introduced_date,
                    last_action_date=doc.last_action_date,
                    sponsor=sponsor_info
                ))
            
            return {
                "total_count": total_count,
                "returned_count": len(document_summaries),
                "offset": skip,
                "limit": limit,
                "documents": document_summaries
            }
            
        except Exception as e:
            logger.error(f"Document listing error: {str(e)}")
            raise