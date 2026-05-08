"""FastAPI application entry point."""

from fastapi import FastAPI

from semantic_router.api.health import router as health_router
from semantic_router.api.routes import router as routes_router
from semantic_router.api.router import router as router_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    application = FastAPI(
        title="SemanticRouter",
        description="A semantic routing layer for safer, more maintainable agentic systems",
        version="0.1.0",
    )
    application.include_router(health_router, prefix="/api/v1", tags=["health"])
    application.include_router(routes_router, prefix="/api/v1", tags=["routes"])
    application.include_router(router_router, prefix="/api/v1", tags=["router"])
    return application


app = create_app()
