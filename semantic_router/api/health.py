"""Health check endpoint."""

from fastapi import APIRouter

from semantic_router.config import settings
from semantic_router.routing.shared import get_registry

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str | int]:
    """Return application health status and configuration summary."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "routes_loaded": len(get_registry().list_routes()),
        "embedding_service": settings.embedding_provider,
    }
