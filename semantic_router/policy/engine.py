"""Policy engine for evaluating route access and constraints."""

import yaml
from pathlib import Path

from pydantic import BaseModel, Field

from semantic_router.models.route import Route


class PolicyDecision(BaseModel):
    """Result of policy evaluation for a route access request."""

    allowed: bool = Field(..., description="Whether the route access is allowed")
    reason: str | None = Field(default=None, description="Reason if access is denied")
    required_action: str | None = Field(
        default=None, description="Action required for access if not immediately allowed"
    )
    missing_permissions: list[str] = Field(
        default_factory=list, description="Permissions the user is missing"
    )


class PolicyEngine:
    """Evaluates routes against policy rules including permissions and approval triggers."""

    def __init__(self) -> None:
        """Initialize the policy engine with empty rules."""
        self._blocked_routes: list[str] = []
        self._permission_map: dict[str, list[str]] = {}
        self._approval_rules: list[dict] = []

    def load_from_yaml(self, path: str | Path) -> None:
        """Load policy rules from a YAML configuration file.

        Args:
            path: Path to the YAML file containing policy definitions.
        """
        file_path = Path(path)
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "policy" not in data:
            return

        policy = data["policy"]
        self._blocked_routes = policy.get("blocked_routes", [])
        self._permission_map = policy.get("permission_map", {})
        self._approval_rules = policy.get("approval_required", [])

    def evaluate(self, route: Route | None, context: dict) -> PolicyDecision:
        """Evaluate whether a route should be allowed for the given context.

        Args:
            route: The selected route to evaluate.
            context: User context including permissions and session data.

        Returns:
            A PolicyDecision indicating whether access is allowed.
        """
        if route is None:
            return PolicyDecision(allowed=False, reason="No route selected")

        if route.name in self._blocked_routes:
            return PolicyDecision(
                allowed=False,
                reason=f"Route '{route.name}' is blocked by policy",
                required_action="contact_admin",
            )

        required = self._permission_map.get(route.name, route.required_permissions)
        if required:
            user_perms = set(context.get("user_permissions", []))
            missing = [p for p in required if p not in user_perms]
            if missing:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Missing required permissions: {', '.join(missing)}",
                    missing_permissions=missing,
                )

        for rule in self._approval_rules:
            if rule.get("route") == route.name:
                return PolicyDecision(
                    allowed=False,
                    reason=rule.get("message", "Approval required"),
                    required_action="request_approval",
                )

        return PolicyDecision(allowed=True)
