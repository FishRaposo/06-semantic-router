"""Pydantic models for route definitions."""

from pydantic import BaseModel, Field


class RouteConfig(BaseModel):
    """Configuration for registering a new route."""

    name: str = Field(..., description="Unique identifier for the route")
    description: str = Field(..., description="Natural-language description for semantic matching")
    tool_name: str = Field(..., description="Name of the tool or workflow to invoke")
    confidence_threshold: float = Field(
        default=0.7, description="Minimum confidence score to auto-select this route"
    )
    required_permissions: list[str] = Field(
        default_factory=list, description="Permissions required to access this route"
    )
    fallback_route: str | None = Field(
        default=None, description="Route to use if confidence is below threshold"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Optional key-value pairs for categorization"
    )


class Route(RouteConfig):
    """A registered route with pre-computed embedding."""

    embedding: list[float] | None = Field(
        default=None, description="Pre-computed embedding vector for the route description"
    )
