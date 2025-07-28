"""
Pydantic schemas for search operations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Types of search operations supported"""
    KEYWORD = "keyword"
    SEMANTIC = "semantic" 
    HYBRID = "hybrid"
    CONVERSATIONAL = "conversational"


class DocumentType(str, Enum):
    """Types of government documents"""
    BILL = "bill"
    EXECUTIVE_ORDER = "executive_order"


class SearchFilters(BaseModel):
    """Filters for search queries"""
    document_type: Optional[DocumentType] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sponsor: Optional[str] = None
    chamber: Optional[str] = Field(None, regex="^(house|senate)$")


class SearchRequest(BaseModel):
    """Request model for document search"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    search_type: SearchType = SearchType.HYBRID
    filters: Optional[SearchFilters] = None
    limit: int = Field(20, ge=1, le=50, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate and sanitize search query"""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for empty query after stripping
        if not v:
            raise ValueError("Query cannot be empty")
            
        return v


class DocumentResult(BaseModel):
    """Individual document in search results"""
    id: str
    identifier: str
    title: str
    summary: Optional[str]
    document_type: DocumentType
    status: Optional[str]
    introduced_date: Optional[datetime]
    last_action_date: Optional[datetime]
    sponsor_name: Optional[str] = None
    sponsor_party: Optional[str] = None
    sponsor_state: Optional[str] = None
    relevance_score: Optional[float] = None
    highlight_snippet: Optional[str] = None
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Response model for document search"""
    query: str
    search_type: SearchType
    total_results: int
    returned_results: int
    response_time_ms: int
    documents: List[DocumentResult]
    filters_applied: Optional[SearchFilters] = None
    suggestions: Optional[List[str]] = None
    
    # AI-generated response for conversational searches
    ai_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    source_documents: Optional[List[str]] = None


class SearchSuggestion(BaseModel):
    """Search suggestion for autocomplete"""
    suggestion: str
    category: str
    popularity_score: float
    expected_results: int


class SearchAnalytics(BaseModel):
    """Search analytics data"""
    query: str
    timestamp: datetime
    search_type: SearchType
    results_count: int
    response_time_ms: int
    user_clicked: bool = False
    filters_used: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True