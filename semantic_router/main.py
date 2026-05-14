"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from semantic_router.api.decisions import router as decisions_router
from semantic_router.api.health import router as health_router
from semantic_router.api.routes import router as routes_router
from semantic_router.api.router import router as router_router
from semantic_router.config import settings
from semantic_router.routing.shared import get_policy_engine, get_registry

logger = logging.getLogger(__name__)


def _load_configs() -> None:
    """Load routes and policies from YAML config files."""
    registry = get_registry()
    routes_path = Path(settings.routes_config)
    if routes_path.exists():
        try:
            registry.load_from_yaml(str(routes_path))
            logger.info("Loaded %d routes from %s", len(registry.list_routes()), routes_path)
        except Exception as exc:
            logger.warning("Failed to load routes from %s: %s", routes_path, exc)
    else:
        logger.info("Routes config not found at %s, starting with empty registry", routes_path)

    policy_engine = get_policy_engine()
    policy_path = Path(settings.policy_config)
    if policy_path.exists():
        try:
            policy_engine.load_from_yaml(str(policy_path))
            logger.info("Loaded policies from %s", policy_path)
        except Exception as exc:
            logger.warning("Failed to load policies from %s: %s", policy_path, exc)
    else:
        logger.info("Policy config not found at %s, starting with empty policies", policy_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    _load_configs()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    application = FastAPI(
        title="SemanticRouter",
        description="A semantic routing layer for safer, more maintainable agentic systems",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router, prefix="/api/v1", tags=["health"])
    application.include_router(routes_router, prefix="/api/v1", tags=["routes"])
    application.include_router(router_router, prefix="/api/v1", tags=["router"])
    application.include_router(decisions_router, prefix="/api/v1", tags=["decisions"])
    return application


app = create_app()
