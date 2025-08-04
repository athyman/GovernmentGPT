#!/usr/bin/env python3
"""
Enhanced FastAPI server with hybrid search and Claude-generated responses
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select, text
from minimal_init import Document
import asyncio
import time
import json
import os
from hybrid_search_service import HybridSearchService

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
    title="GovernmentGPT Enhanced API",
    description="Government document search with hybrid semantic + keyword search and Claude-generated responses",
    version="0.3.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize hybrid search service
claude_api_key = os.getenv('CLAUDE_API_KEY')
search_service = HybridSearchService(claude_api_key=claude_api_key)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = "conversational"
    limit: Optional[int] = 10
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
    sponsor: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    relevance_score: Optional[float] = 1.0

class ConversationalSearchResponse(BaseModel):
    query: str
    search_type: str
    claude_response: str
    confidence: float
    suggestions: List[str]
    total_results: int
    returned_results: int
    response_time_ms: int
    documents: List[DocumentResult]

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
        # Get document counts by type
        bill_count = await db.execute(
            select(Document).where(Document.document_type == 'bill')
        )
        bills = len(bill_count.scalars().all())
        
        eo_count = await db.execute(
            select(Document).where(Document.document_type == 'executive_order')
        )
        eos = len(eo_count.scalars().all())
        
        total_count = bills + eos
    
    return {
        "status": "healthy",
        "database": "connected",
        "total_documents": total_count,
        "bills": bills,
        "executive_orders": eos,
        "features": ["conversational_search", "claude_responses", "enhanced_search"],
        "message": "GovernmentGPT Enhanced API is running"
    }

@app.post("/api/v1/search", response_model=ConversationalSearchResponse)
async def enhanced_search(request: SearchRequest):
    """Enhanced hybrid search with Claude-generated responses"""
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        # Use hybrid search service for comprehensive results
        search_result = await search_service.search_with_ai_response(
            query=request.query, 
            limit=request.limit
        )
        
        # Convert documents to response format
        results = []
        for doc in search_result.get('documents', []):
            results.append(DocumentResult(
                id=doc['id'],
                identifier=doc['identifier'],
                title=doc['title'],
                summary=doc.get('summary', '') or '',
                document_type=doc['document_type'],
                status=doc.get('status', '') or '',
                introduced_date=doc.get('introduced_date'),
                last_action_date=doc.get('last_action_date'),
                sponsor=doc.get('sponsor'),
                metadata=doc.get('metadata', {}),
                relevance_score=doc.get('relevance_score', 1.0)
            ))
        
        return ConversationalSearchResponse(
            query=search_result['query'],
            search_type=search_result.get('search_type', 'hybrid'),
            claude_response=search_result['claude_response'],
            confidence=search_result['confidence'],
            suggestions=search_result.get('suggestions', []),
            total_results=search_result.get('total_results', len(results)),
            returned_results=len(results),
            response_time_ms=search_result.get('execution_time_ms', 0),
            documents=results
        )
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/v1/search/simple", response_model=SearchResponse)
async def simple_search(request: SearchRequest):
    """Simple search without Claude responses (for backward compatibility)"""
    start_time = time.time()
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        # Use hybrid search but only return documents
        documents = await search_service.hybrid_search(request.query, limit=request.limit)
        
        # Convert documents to response format
        results = []
        for doc in documents:
            results.append(DocumentResult(
                id=doc['id'],
                identifier=doc['identifier'],
                title=doc['title'],
                summary=doc.get('summary', '') or '',
                document_type=doc['document_type'],
                status=doc.get('status', '') or '',
                introduced_date=doc.get('introduced_date'),
                last_action_date=doc.get('last_action_date'),
                sponsor=doc.get('sponsor'),
                metadata=doc.get('metadata', {}),
                relevance_score=doc.get('relevance_score', 1.0)
            ))
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return SearchResponse(
            query=request.query,
            search_type="hybrid",
            total_results=len(documents),
            returned_results=len(results),
            response_time_ms=execution_time,
            documents=results
        )
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

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
        # Parse metadata first
        metadata = {}
        sponsor_data = None
        if doc.doc_metadata:
            try:
                metadata = json.loads(doc.doc_metadata) if isinstance(doc.doc_metadata, str) else doc.doc_metadata
                # Extract sponsor from metadata
                if isinstance(metadata, dict) and 'sponsor' in metadata:
                    sponsor_data = metadata['sponsor']
            except Exception as e:
                print(f"Error parsing metadata: {e}")
                metadata = {}
        
        document_list.append({
            "id": doc.id,
            "identifier": doc.identifier,
            "title": doc.title,
            "summary": doc.summary or "",
            "document_type": doc.document_type,
            "status": doc.status or "",
            "introduced_date": doc.introduced_date.isoformat() if doc.introduced_date else None,
            "last_action_date": doc.last_action_date.isoformat() if doc.last_action_date else None,
            "sponsor": sponsor_data,
            "metadata": metadata
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
        
        # Parse metadata first
        metadata = {}
        sponsor_data = None
        if document.doc_metadata:
            try:
                metadata = json.loads(document.doc_metadata) if isinstance(document.doc_metadata, str) else document.doc_metadata
                # Extract sponsor from metadata
                if isinstance(metadata, dict) and 'sponsor' in metadata:
                    sponsor_data = metadata['sponsor']
            except Exception as e:
                print(f"Error parsing metadata: {e}")
                metadata = {}
        
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
            "sponsor": sponsor_data,
            "metadata": metadata,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
        return doc_response

@app.get("/api/v1/search/test")
async def test_search_queries():
    """Test various search queries to verify functionality"""
    test_queries = [
        "infrastructure bill",
        "one big beautiful bill act", 
        "climate change",
        "healthcare",
        "defense authorization",
        "veterans affairs"
    ]
    
    results = {}
    
    for query in test_queries:
        try:
            # Use the hybrid search service's comprehensive search method
            search_result = await search_service.search_with_ai_response(query, limit=3)
            
            results[query] = {
                "documents_found": search_result.get('total_results', 0),
                "confidence": search_result.get('confidence', 0.0),
                "sample_titles": [doc.get('title', '')[:100] for doc in search_result.get('documents', [])[:2]],
                "execution_time_ms": search_result.get('execution_time_ms', 0)
            }
        except Exception as e:
            results[query] = {"error": str(e)}
    
    return {
        "test_results": results,
        "message": "Search functionality test complete"
    }

@app.get("/api/v1/stats")
async def get_statistics():
    """Get platform statistics"""
    async with AsyncSessionLocal() as db:
        # Document counts
        bill_count = await db.execute(
            text("SELECT COUNT(*) FROM documents WHERE document_type = 'bill'")
        )
        bills = bill_count.scalar()
        
        eo_count = await db.execute(
            text("SELECT COUNT(*) FROM documents WHERE document_type = 'executive_order'")
        )
        eos = eo_count.scalar()
        
        # Recent activity
        recent_bills = await db.execute(
            text("SELECT COUNT(*) FROM documents WHERE document_type = 'bill' AND introduced_date >= date('now', '-30 days')")
        )
        recent_bill_count = recent_bills.scalar()
        
        # Status breakdown for bills
        status_breakdown = await db.execute(
            text("SELECT status, COUNT(*) as count FROM documents WHERE document_type = 'bill' GROUP BY status ORDER BY count DESC")
        )
        status_data = [{"status": row[0] or "Unknown", "count": row[1]} for row in status_breakdown.fetchall()]
        
        return {
            "total_documents": bills + eos,
            "bills": bills,
            "executive_orders": eos,
            "recent_bills_30_days": recent_bill_count,
            "status_breakdown": status_data[:10],  # Top 10 statuses
            "last_updated": "real-time"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced GovernmentGPT Server with Claude integration...")
    uvicorn.run(
        "enhanced_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )