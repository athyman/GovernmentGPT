"""
API routes for GovernmentGPT.
Defines all endpoint routes and organizes them into logical groups.
"""

from fastapi import APIRouter
from app.api.endpoints import search, documents, health

# Main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)