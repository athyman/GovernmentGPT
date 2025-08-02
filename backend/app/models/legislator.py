"""
Legislator models for GovernmentGPT.
Represents members of Congress and their information.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Legislator(Base):
    """
    Member of Congress information from Bioguide and other sources.
    """
    __tablename__ = 'legislators'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bioguide_id = Column(String(10), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    party = Column(String(20))  # 'D', 'R', 'I', etc.
    state = Column(String(2))   # Two-letter state code
    district = Column(String(10))  # For House members, null for Senators
    chamber = Column(String(10), nullable=False)  # 'house' or 'senate'
    active = Column(Boolean, default=True)
    
    # Terms and service information
    first_service_date = Column(DateTime)
    last_service_date = Column(DateTime)
    
    # Contact and biographical information
    official_website = Column(String(255))
    twitter_account = Column(String(100))
    youtube_account = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sponsored_documents = relationship("Document", back_populates="sponsor")
    
    # Indexes
    __table_args__ = (
        Index('idx_legislators_active', 'active', 'chamber'),
        Index('idx_legislators_state_party', 'state', 'party'),
        Index('idx_legislators_name', 'last_name', 'first_name'),
    )
    
    @property
    def display_name(self) -> str:
        """Full display name with party and state"""
        party_state = f"({self.party}-{self.state})" if self.party and self.state else ""
        return f"{self.full_name} {party_state}".strip()
    
    @property
    def is_senator(self) -> bool:
        """Check if legislator is a Senator"""
        return self.chamber == 'senate'
    
    @property
    def is_representative(self) -> bool:
        """Check if legislator is a House Representative"""
        return self.chamber == 'house'
    
    def __repr__(self):
        return f"<Legislator {self.bioguide_id}: {self.full_name} ({self.party}-{self.state})>"


class LegislatorTerm(Base):
    """
    Individual terms of service for legislators.
    Tracks when they served and in what capacity.
    """
    __tablename__ = 'legislator_terms'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legislator_id = Column(String(36), ForeignKey('legislators.id'), nullable=False)
    chamber = Column(String(10), nullable=False)  # 'house' or 'senate'
    state = Column(String(2), nullable=False)
    district = Column(String(10))  # For House terms
    party = Column(String(20))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Term metadata
    congress_number = Column(Integer)  # e.g., 118 for 118th Congress
    term_type = Column(String(20))  # 'full', 'partial', 'special'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    legislator = relationship("Legislator")
    
    __table_args__ = (
        Index('idx_legislator_terms_dates', 'legislator_id', 'start_date', 'end_date'),
        Index('idx_legislator_terms_congress', 'congress_number', 'chamber'),
    )
    
    def __repr__(self):
        return f"<LegislatorTerm {self.legislator_id}:{self.congress_number}>"