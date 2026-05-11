"""Route management endpoints."""

from fastapi import APIRouter, HTTPException

from semantic_router.models.route import Route, RouteConfig
from semantic_router.routing.shared import get_registry

router = APIRouter()

registry = get_registry()


@router.get("/routes", response_model=list[Route])
async def list_routes() -> list[Route]:
    """Return all registered routes."""
    return registry.list_routes()


@router.post("/routes", response_model=Route, status_code=201)
async def register_route(route_config: RouteConfig) -> Route:
    """Register a new route in the registry."""
    existing = registry.get_route(route_config.name)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Route '{route_config.name}' already exists")
    route = Route(**route_config.model_dump())
    registry.register_route(route)
    return route


@router.delete("/routes/{name}", status_code=204)
async def remove_route(name: str) -> None:
    """Remove a route from the registry."""
    removed = registry.remove_route(name)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Route '{name}' not found")
