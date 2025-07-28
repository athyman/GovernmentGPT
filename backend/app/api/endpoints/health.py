"""
Health check endpoints for GovernmentGPT API.
Provides application health and readiness status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import time
from typing import Dict, Any

from app.core.database import get_db, DatabaseManager

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "GovernmentGPT API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check with database connectivity"""
    
    # Check database connection
    db_healthy = await DatabaseManager.health_check()
    
    status = "ready" if db_healthy else "not_ready"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy"
        }
    }


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Basic metrics endpoint"""
    # TODO: Implement Prometheus metrics
    return {
        "timestamp": time.time(),
        "metrics": {
            "requests_total": 0,
            "response_time_avg": 0.0,
            "active_connections": 0
        }
    }