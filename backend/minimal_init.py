#!/usr/bin/env python3
"""
Minimal database initialization for data ingestion testing
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Date, DateTime, JSON, Index
from sqlalchemy.pool import StaticPool
import uuid
from datetime import datetime

# Create base
Base = declarative_base()

# Minimal Document model for ingestion
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_type = Column(String(20), nullable=False)
    identifier = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    full_text = Column(Text, nullable=False)
    status = Column(String(50))
    introduced_date = Column(Date)
    last_action_date = Column(Date)
    sponsor_id = Column(String(36))
    doc_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_documents_identifier', 'document_type', 'identifier', unique=True),
    )

# Minimal Legislator model
class Legislator(Base):
    __tablename__ = 'legislators'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bioguide_id = Column(String(10), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    party = Column(String(20))
    state = Column(String(2))
    district = Column(String(10))
    chamber = Column(String(10), nullable=False)
    active = Column(String(10), default="true")  # Use string for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)

async def create_minimal_db():
    """Create minimal database for testing"""
    DATABASE_URL = "sqlite+aiosqlite:///./governmentgpt_local.db"
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Minimal database created successfully")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_minimal_db())