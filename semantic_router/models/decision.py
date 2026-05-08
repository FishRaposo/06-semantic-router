"""Pydantic models for routing decisions and execution results."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from semantic_router.models.request import RoutingRequest


class PolicyCheck(BaseModel):
    """Result of policy evaluation for a route."""

    allowed: bool = Field(..., description="Whether the route access is allowed")
    reason: str | None = Field(default=None, description="Reason if access is denied")
    required_action: str | None = Field(default=None, description="Action required if not allowed")
    missing_permissions: list[str] = Field(
        default_factory=list, description="Permissions the user is missing"
    )


class ExecutionResult(BaseModel):
    """Result of executing a tool after routing."""

    tool_name: str = Field(..., description="Name of the tool that was executed")
    status: str = Field(default="success", description="Execution status: success or error")
    data: dict | None = Field(default=None, description="Data returned by the tool")
    error: str | None = Field(default=None, description="Error message if execution failed")


class RoutingDecision(BaseModel):
    """The result of routing a user query to a tool."""

    selected_route: str | None = Field(
        default=None, description="Name of the selected route, or None if no match"
    )
    confidence: float = Field(
        default=0.0, description="Confidence score for the selected route"
    )
    rejected_routes: list[dict[str, str | float]] = Field(
        default_factory=list, description="Routes considered but not selected with their scores"
    )
    policy_check: PolicyCheck | None = Field(
        default=None, description="Result of policy evaluation"
    )
    fallback_used: bool = Field(
        default=False, description="Whether a fallback route was used"
    )
    clarification: str | None = Field(
        default=None, description="Clarification prompt if confidence is low"
    )
    execution_result: ExecutionResult | None = Field(
        default=None, description="Result from tool execution"
    )


class DecisionLog(BaseModel):
    """A logged record of a routing decision."""

    request: RoutingRequest = Field(..., description="The original routing request")
    decision: RoutingDecision = Field(..., description="The routing decision made")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the decision was made",
    )
    processing_time_ms: int = Field(
        ..., description="Time taken to make the routing decision in milliseconds"
    )
