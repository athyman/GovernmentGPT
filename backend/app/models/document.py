"""
Document models for GovernmentGPT.
Represents congressional bills and executive orders.
"""

from sqlalchemy import Column, String, Text, Date, DateTime, Boolean, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.core.database import Base


class Document(Base):
    """
    Core document model for bills and executive orders.
    Stores full text content and metadata from government sources.
    """
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_type = Column(String(20), nullable=False)  # 'bill' or 'executive_order'
    identifier = Column(String(50), nullable=False)  # e.g., 'HR-1234-118' or 'EO-14000'
    title = Column(Text, nullable=False)
    summary = Column(Text)
    full_text = Column(Text, nullable=False)
    status = Column(String(50))
    introduced_date = Column(Date)
    last_action_date = Column(Date)
    sponsor_id = Column(String(36), ForeignKey('legislators.id'))
    doc_metadata = Column(JSON, default={})  # Flexible storage for varying government data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sponsor = relationship("Legislator", back_populates="sponsored_documents")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes (SQLite compatible)
    __table_args__ = (
        Index('idx_documents_type_date', 'document_type', 'introduced_date'),
        Index('idx_documents_identifier', 'document_type', 'identifier', unique=True),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_title', 'title'),
    )
    
    def __repr__(self):
        return f"<Document {self.identifier}: {self.title[:50]}...>"


class DocumentEmbedding(Base):
    """
    Vector embeddings for semantic search of document chunks.
    Uses Voyage-law-2 embeddings (1024 dimensions).
    """
    __tablename__ = 'document_embeddings'
    
    document_id = Column(String(36), ForeignKey('documents.id'), primary_key=True)
    chunk_index = Column(Integer, primary_key=True)
    chunk_text = Column(Text, nullable=False)
    # Note: vector type requires pgvector extension
    # embedding = Column(Vector(1024))  # Will be added when pgvector is available
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    
    def __repr__(self):
        return f"<DocumentEmbedding {self.document_id}:{self.chunk_index}>"


class DocumentVersion(Base):
    """
    Track different versions of documents as they progress through legislature.
    """
    __tablename__ = 'document_versions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False)
    version_number = Column(String(20), nullable=False)  # e.g., 'ih', 'eh', 'enr'
    version_date = Column(Date, nullable=False)
    full_text = Column(Text, nullable=False)
    changes_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document")
    
    __table_args__ = (
        Index('idx_document_versions_doc_version', 'document_id', 'version_number', unique=True),
    )
    
    def __repr__(self):
        return f"<DocumentVersion {self.document_id}:{self.version_number}>"