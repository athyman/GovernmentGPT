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
    limit: Optional[int] = 20

class DocumentResult(BaseModel):
    id: str
    identifier: str
    title: str
    summary: str
    document_type: str
    status: str
    introduced_date: Optional[str]
    last_action_date: Optional[str]

class SearchResponse(BaseModel):
    query: str
    results: List[DocumentResult]
    total_count: int
    execution_time_ms: int

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

@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search government documents"""
    import time
    start_time = time.time()
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    query = request.query.strip().lower()
    
    async with AsyncSessionLocal() as db:
        # Simple text search across title and summary
        stmt = select(Document).where(
            or_(
                Document.title.ilike(f"%{query}%"),
                Document.summary.ilike(f"%{query}%"),
                Document.identifier.ilike(f"%{query}%")
            )
        ).limit(request.limit)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        # Get total count for different query
        count_stmt = select(Document).where(
            or_(
                Document.title.ilike(f"%{query}%"),
                Document.summary.ilike(f"%{query}%"),
                Document.identifier.ilike(f"%{query}%")
            )
        )
        count_result = await db.execute(count_stmt)
        total_count = len(count_result.scalars().all())
    
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
            last_action_date=doc.last_action_date.isoformat() if doc.last_action_date else None
        ))
    
    execution_time = int((time.time() - start_time) * 1000)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total_count=total_count,
        execution_time_ms=execution_time
    )

@app.get("/api/documents/stats")
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