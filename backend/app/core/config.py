"""
Configuration settings for GovernmentGPT application.
Uses Pydantic settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/governmentgpt"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 900  # 15 minutes default
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000"
    ]
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = None
    VOYAGE_API_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    
    # Government APIs
    CONGRESS_API_KEY: Optional[str] = None
    GOVTRACK_API_BASE: str = "https://www.govtrack.us/api/v2"
    FEDERAL_REGISTER_API_BASE: str = "https://www.federalregister.gov/api/v1"
    GOVINFO_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Search Configuration
    SEARCH_RESULTS_LIMIT: int = 50
    SEMANTIC_SEARCH_TOP_K: int = 50
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Content Processing
    MAX_DOCUMENT_SIZE: int = 1_000_000  # 1MB
    SUMMARY_MAX_LENGTH: int = 1500
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()