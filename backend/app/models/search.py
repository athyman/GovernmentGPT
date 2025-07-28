"""
Search-related models for GovernmentGPT.
Handles search analytics and caching.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class SearchCache(Base):
    """
    Cache search results to improve performance.
    """
    __tablename__ = 'search_cache'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash of query + filters
    original_query = Column(Text, nullable=False)
    search_type = Column(String(20), nullable=False)  # 'semantic', 'keyword', 'hybrid'
    filters = Column(JSONB, default={})
    
    # Cached results
    results = Column(JSONB, nullable=False)
    results_count = Column(Integer, nullable=False)
    
    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    expires_at = Column(DateTime, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_search_cache_hash', 'query_hash'),
        Index('idx_search_cache_expires', 'expires_at'),
        Index('idx_search_cache_accessed', 'last_accessed'),
    )
    
    def __repr__(self):
        return f"<SearchCache {self.query_hash[:8]}...>"


class SearchAnalytics(Base):
    """
    Aggregate search analytics for insights and optimization.
    """
    __tablename__ = 'search_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False)  # Date for aggregation (daily)
    
    # Query patterns
    query_text = Column(Text)  # Popular queries
    query_frequency = Column(Integer, default=1)
    
    # Performance metrics
    avg_response_time_ms = Column(Float)
    avg_results_count = Column(Float)
    
    # User behavior
    click_through_rate = Column(Float)
    zero_result_rate = Column(Float)
    
    # Search types
    search_type = Column(String(20))
    user_type = Column(String(20))  # 'authenticated', 'anonymous'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_search_analytics_date', 'date'),
        Index('idx_search_analytics_query_freq', 'query_frequency'),
        Index('idx_search_analytics_type_date', 'search_type', 'date'),
    )
    
    def __repr__(self):
        return f"<SearchAnalytics {self.date.strftime('%Y-%m-%d')}:{self.query_text[:20]}...>"


class PopularSearches(Base):
    """
    Track and rank popular search queries for suggestions.
    """
    __tablename__ = 'popular_searches'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False, unique=True)
    normalized_query = Column(Text, nullable=False)  # Lowercase, trimmed version
    
    # Popularity metrics
    search_count = Column(Integer, default=1)
    recent_searches = Column(Integer, default=1)  # Last 7 days
    success_rate = Column(Float, default=1.0)  # % of searches that had results
    
    # Query metadata
    avg_results_count = Column(Float)
    first_searched = Column(DateTime, default=datetime.utcnow)
    last_searched = Column(DateTime, default=datetime.utcnow)
    
    # Categories and tags
    categories = Column(JSONB, default=[])  # e.g., ['healthcare', 'environment']
    is_trending = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_popular_searches_count', 'search_count'),
        Index('idx_popular_searches_recent', 'recent_searches'),
        Index('idx_popular_searches_normalized', 'normalized_query'),
        Index('idx_popular_searches_trending', 'is_trending', 'search_count'),
    )
    
    def __repr__(self):
        return f"<PopularSearches {self.query[:30]}... ({self.search_count} searches)>"


class SearchSuggestions(Base):
    """
    Pre-computed search suggestions for autocomplete.
    """
    __tablename__ = 'search_suggestions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suggestion = Column(Text, nullable=False)
    category = Column(String(50))  # 'legislation', 'topic', 'person', 'agency'
    
    # Suggestion metadata
    popularity_score = Column(Float, default=0.0)
    result_count = Column(Integer, default=0)  # Expected number of results
    
    # Context and matching
    keywords = Column(JSONB, default=[])  # Keywords for matching
    synonyms = Column(JSONB, default=[])  # Alternative terms
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_search_suggestions_text', 'suggestion'),
        Index('idx_search_suggestions_category', 'category', 'popularity_score'),
        Index('idx_search_suggestions_active', 'is_active', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<SearchSuggestions {self.suggestion[:30]}... (score: {self.popularity_score})>"