"""
User models for GovernmentGPT.
Handles user authentication and session management.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import secrets

from app.core.database import Base


class User(Base):
    """
    User account information with authentication details.
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))  # Nullable for OAuth-only users
    verified_citizen = Column(Boolean, default=False)
    notification_preferences = Column(JSONB, default={})
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("UserSearchHistory", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_verified', 'is_verified'),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserSession(Base):
    """
    User session management for authentication.
    """
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Session metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_sessions_token', 'session_token'),
        Index('idx_user_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_user_sessions_expires', 'expires_at'),
    )
    
    @classmethod
    def create_session(cls, user_id: uuid.UUID, days: int = 7) -> 'UserSession':
        """Create a new user session with secure token"""
        return cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=days)
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def refresh(self, days: int = 7):
        """Refresh session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(days=days)
        self.last_used = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserSession {self.user_id}:{self.session_token[:8]}...>"


class UserSearchHistory(Base):
    """
    Track user search queries for analytics and personalization.
    """
    __tablename__ = 'user_search_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # Nullable for anonymous users
    session_id = Column(String(255))  # For anonymous users
    query = Column(Text, nullable=False)
    results_count = Column(Integer)
    search_timestamp = Column(DateTime, default=datetime.utcnow)
    search_type = Column(String(20))  # 'semantic', 'keyword', 'hybrid', 'conversational'
    
    # Search metadata
    filters_applied = Column(JSONB, default={})
    response_time_ms = Column(Integer)
    user_clicked_result = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_search_history_user_time', 'user_id', 'search_timestamp'),
        Index('idx_search_history_session_time', 'session_id', 'search_timestamp'),
        Index('idx_search_history_query_text', 'query', postgresql_using='gin'),
        Index('idx_search_history_type_time', 'search_type', 'search_timestamp'),
    )
    
    def __repr__(self):
        return f"<UserSearchHistory {self.query[:30]}...>"


class EmailVerification(Base):
    """
    Email verification tokens for user registration.
    """
    __tablename__ = 'email_verifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_email_verification_token', 'token'),
        Index('idx_email_verification_expires', 'expires_at'),
    )
    
    @classmethod
    def create_verification(cls, user_id: uuid.UUID, hours: int = 24) -> 'EmailVerification':
        """Create a new email verification token"""
        return cls(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=hours)
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if verification token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<EmailVerification {self.user_id}:{self.token[:8]}...>"