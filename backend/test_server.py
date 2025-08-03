#!/usr/bin/env python3
"""
Minimal FastAPI server for testing search functionality with real data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select, or_, and_
from minimal_init import Document, Legislator
import asyncio

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

# FastAPI app
app = FastAPI(
    title="GovernmentGPT Test API",
    description="Testing government document search with real data",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = "keyword"
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class DocumentResult(BaseModel):
    id: str
    identifier: str
    title: str
    summary: str
    document_type: str
    status: str
    introduced_date: Optional[str]
    last_action_date: Optional[str]
    relevance_score: Optional[float] = 1.0

class SearchResponse(BaseModel):
    query: str
    search_type: str
    total_results: int
    returned_results: int
    response_time_ms: int
    documents: List[DocumentResult]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    async with AsyncSessionLocal() as db:
        total_docs = await db.execute(select(Document))
        count = len(total_docs.scalars().all())
    
    return {
        "status": "healthy",
        "database": "connected",
        "total_documents": count,
        "message": "GovernmentGPT Test API is running"
    }

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search government documents with enhanced search capabilities"""
    import time
    from semantic_search import EnhancedSearchService
    
    start_time = time.time()
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    # Use enhanced search service
    search_service = EnhancedSearchService()
    documents, total_count = await search_service.enhanced_search(
        query=request.query,
        limit=request.limit,
        offset=request.offset or 0
    )
    
    # Convert to response format
    results = []
    for doc in documents:
        results.append(DocumentResult(
            id=doc.id,
            identifier=doc.identifier,
            title=doc.title,
            summary=doc.summary or "",
            document_type=doc.document_type,
            status=doc.status or "",
            introduced_date=doc.introduced_date.isoformat() if doc.introduced_date else None,
            last_action_date=doc.last_action_date.isoformat() if doc.last_action_date else None,
            relevance_score=1.0
        ))
    
    execution_time = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        search_type=request.search_type or "enhanced_keyword",
        total_results=total_count,
        returned_results=len(results),
        response_time_ms=execution_time,
        documents=results
    )

@app.get("/api/v1/search/recent")
async def get_recent_documents(limit: int = 10, document_type: Optional[str] = None):
    """Get recent government documents"""
    async with AsyncSessionLocal() as db:
        # Get recent documents ordered by last_action_date
        stmt = select(Document)
        
        if document_type:
            stmt = stmt.where(Document.document_type == document_type)
        
        stmt = stmt.order_by(Document.last_action_date.desc()).limit(limit)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
    
    # Convert to response format
    document_list = []
    for doc in documents:
        document_list.append({
            "id": doc.id,
            "identifier": doc.identifier,
            "title": doc.title,
            "summary": doc.summary or "",
            "document_type": doc.document_type,
            "status": doc.status or "",
            "introduced_date": doc.introduced_date.isoformat() if doc.introduced_date else None,
            "last_action_date": doc.last_action_date.isoformat() if doc.last_action_date else None
        })
    
    return {"documents": document_list}

@app.get("/api/v1/documents/{document_identifier}")
async def get_document(document_identifier: str):
    """Get detailed information for a specific document"""
    async with AsyncSessionLocal() as db:
        # Search by identifier
        stmt = select(Document).where(Document.identifier == document_identifier)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert to detailed response format
        doc_response = {
            "id": document.id,
            "identifier": document.identifier,
            "title": document.title,
            "summary": document.summary or "",
            "full_text": document.full_text or document.title,
            "document_type": document.document_type,
            "status": document.status or "",
            "introduced_date": document.introduced_date.isoformat() if document.introduced_date else None,
            "last_action_date": document.last_action_date.isoformat() if document.last_action_date else None,
            "sponsor": None,  # Will be populated if sponsor_id exists
            "metadata": document.doc_metadata or {},
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
        return doc_response

@app.get("/api/v1/documents/stats")
async def document_stats():
    """Get document statistics"""
    async with AsyncSessionLocal() as db:
        # Count by type
        all_docs = await db.execute(select(Document))
        documents = all_docs.scalars().all()
        
        stats = {
            "total_documents": len(documents),
            "bills": len([d for d in documents if d.document_type == "bill"]),
            "executive_orders": len([d for d in documents if d.document_type == "executive_order"]),
            "presidential_documents": len([d for d in documents if d.document_type == "presidential_document"]),
            "recent_bills": len([d for d in documents if d.document_type == "bill" and d.introduced_date and d.introduced_date.year == 2024]),
        }
        
        return stats

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GovernmentGPT Test API",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "stats": "/api/documents/stats",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)