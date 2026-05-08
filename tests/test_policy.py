"""Tests for the PolicyEngine."""

import tempfile
from pathlib import Path

import pytest
import yaml

from semantic_router.models.route import Route
from semantic_router.policy.engine import PolicyDecision, PolicyEngine


@pytest.fixture
def policy_engine() -> PolicyEngine:
    """Provide a policy engine with standard rules."""
    engine = PolicyEngine()
    engine._blocked_routes = []
    engine._permission_map = {
        "invoice_lookup": ["billing.read"],
        "support_ticket": ["support.read"],
        "refund_request": ["billing.write", "finance.approve"],
        "policy_question": [],
        "sales_lead": ["sales.read"],
    }
    return engine


class TestPolicyEngine:
    """Tests for policy evaluation of route access."""

    def test_allow_with_permissions(self, policy_engine: PolicyEngine) -> None:
        """A route is allowed when the user has all required permissions."""
        route = Route(
            name="invoice_lookup",
            description="Look up invoices",
            tool_name="invoice_lookup",
            confidence_threshold=0.7,
            required_permissions=["billing.read"],
        )
        context = {"user_permissions": ["billing.read"]}
        result = policy_engine.evaluate(route=route, context=context)
        assert result.allowed is True

    def test_deny_missing_permissions(self, policy_engine: PolicyEngine) -> None:
        """A route is denied when the user is missing required permissions."""
        route = Route(
            name="refund_request",
            description="Request a refund",
            tool_name="refund_request",
            confidence_threshold=0.8,
            required_permissions=["billing.write", "finance.approve"],
        )
        context = {"user_permissions": ["billing.read"]}
        result = policy_engine.evaluate(route=route, context=context)
        assert result.allowed is False
        assert len(result.missing_permissions) == 2

    def test_deny_blocked_route(self, policy_engine: PolicyEngine) -> None:
        """A blocked route is denied regardless of permissions."""
        policy_engine._blocked_routes = ["refund_request"]
        route = Route(
            name="refund_request",
            description="Request a refund",
            tool_name="refund_request",
            confidence_threshold=0.8,
            required_permissions=[],
        )
        context = {"user_permissions": []}
        result = policy_engine.evaluate(route=route, context=context)
        assert result.allowed is False
        assert "blocked" in (result.reason or "").lower()

    def test_allow_no_permissions_required(self, policy_engine: PolicyEngine) -> None:
        """A route with no required permissions is allowed for everyone."""
        route = Route(
            name="policy_question",
            description="Ask about policies",
            tool_name="policy_question",
            confidence_threshold=0.6,
            required_permissions=[],
        )
        context = {"user_permissions": []}
        result = policy_engine.evaluate(route=route, context=context)
        assert result.allowed is True

    def test_evaluate_none_route(self, policy_engine: PolicyEngine) -> None:
        """Evaluating with None route returns not allowed."""
        result = policy_engine.evaluate(route=None, context={})
        assert result.allowed is False

    def test_approval_trigger(self, policy_engine: PolicyEngine) -> None:
        """A route with an approval trigger is denied with the approval message."""
        policy_engine._approval_rules = [
            {"route": "refund_request", "condition": "amount > 500", "message": "Manager approval needed"},
        ]
        route = Route(
            name="refund_request",
            description="Request a refund",
            tool_name="refund_request",
            confidence_threshold=0.8,
            required_permissions=["billing.write", "finance.approve"],
        )
        context = {"user_permissions": ["billing.write", "finance.approve"]}
        result = policy_engine.evaluate(route=route, context=context)
        assert result.allowed is False
        assert result.required_action == "request_approval"

    def test_load_from_yaml(self) -> None:
        """Policy rules can be loaded from a YAML file."""
        yaml_data = {
            "policy": {
                "blocked_routes": ["blocked_route"],
                "permission_map": {"route_a": ["perm.read"]},
                "approval_required": [],
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.dump(yaml_data, f)
            f.flush()
            path = f.name

        try:
            engine = PolicyEngine()
            engine.load_from_yaml(path)
            assert engine._blocked_routes == ["blocked_route"]
            assert engine._permission_map == {"route_a": ["perm.read"]}
        finally:
            Path(path).unlink(missing_ok=True)
