"""Pydantic models for routing requests."""

from pydantic import BaseModel, Field


class RoutingRequest(BaseModel):
    """A request to route a user query to the appropriate tool."""

    query: str = Field(..., description="The user's natural-language query")
    context: dict | None = Field(
        default=None, description="Optional context including user permissions and session data"
    )
    user_id: str | None = Field(default=None, description="Identifier for the requesting user")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional metadata for the request"
    )


class RoutingContext(BaseModel):
    """Context for a routing decision including user permissions and history."""

    user_permissions: list[str] = Field(
        default_factory=list, description="Permissions granted to the user"
    )
    request_history: list[str] = Field(
        default_factory=list, description="Recent route names from this session"
    )
    session_data: dict[str, str] = Field(
        default_factory=dict, description="Session-specific key-value data"
    )
