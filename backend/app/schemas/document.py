"""
Pydantic schemas for document operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

from app.schemas.search import DocumentType


class DocumentStatus(str, Enum):
    """Status values for legislative documents"""
    INTRODUCED = "introduced"
    REFERRED = "referred"
    REPORTED = "reported"
    PASSED_HOUSE = "passed_house"
    PASSED_SENATE = "passed_senate"
    PASSED = "passed"
    SIGNED = "signed"
    VETOED = "vetoed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"


class LegislatorInfo(BaseModel):
    """Basic legislator information"""
    id: str
    bioguide_id: str
    full_name: str
    party: Optional[str]
    state: Optional[str]
    district: Optional[str] = None
    chamber: str
    
    class Config:
        from_attributes = True


class DocumentSummary(BaseModel):
    """Condensed document information for listings"""
    id: str
    identifier: str
    title: str
    summary: Optional[str]
    document_type: DocumentType
    status: Optional[str]
    introduced_date: Optional[date]
    last_action_date: Optional[date]
    sponsor: Optional[LegislatorInfo] = None
    
    class Config:
        from_attributes = True


class DocumentVersion(BaseModel):
    """Document version information"""
    version_number: str
    version_date: date
    changes_summary: Optional[str]
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Full document details"""
    id: str
    identifier: str
    title: str
    summary: Optional[str]
    full_text: str
    document_type: DocumentType
    status: Optional[str]
    introduced_date: Optional[date]
    last_action_date: Optional[date]
    sponsor: Optional[LegislatorInfo] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    text_length: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    versions: Optional[List[DocumentVersion]] = None
    
    class Config:
        from_attributes = True
    
    @property
    def text_length(self) -> int:
        """Calculate text length"""
        return len(self.full_text) if self.full_text else 0
    
    @property 
    def reading_time_minutes(self) -> int:
        """Estimate reading time (average 200 words per minute)"""
        if not self.full_text:
            return 0
        word_count = len(self.full_text.split())
        return max(1, round(word_count / 200))


class DocumentCreate(BaseModel):
    """Schema for creating new documents"""
    identifier: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1)
    summary: Optional[str] = None
    full_text: str = Field(..., min_length=1)
    document_type: DocumentType
    status: Optional[str] = None
    introduced_date: Optional[date] = None
    last_action_date: Optional[date] = None
    sponsor_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentUpdate(BaseModel):
    """Schema for updating existing documents"""
    title: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    full_text: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = None
    last_action_date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentListResponse(BaseModel):
    """Response for document listing endpoints"""
    total_count: int
    returned_count: int
    offset: int
    limit: int
    documents: List[DocumentSummary]
    
    class Config:
        from_attributes = True