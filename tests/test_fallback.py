"""Tests for the FallbackHandler."""

import pytest

from semantic_router.models.decision import PolicyCheck, RoutingDecision
from semantic_router.models.request import RoutingRequest
from semantic_router.policy.fallback import FallbackHandler


@pytest.fixture
def handler() -> FallbackHandler:
    """Provide a fallback handler instance."""
    return FallbackHandler()


@pytest.fixture
def sample_request() -> RoutingRequest:
    """Provide a sample routing request."""
    return RoutingRequest(query="I need help", user_id="user-1")


class TestFallbackHandler:
    """Tests for fallback handling in various failure scenarios."""

    def test_handle_no_match(self, handler: FallbackHandler, sample_request: RoutingRequest) -> None:
        """No match returns a decision with clarification and no selected route."""
        result = handler.handle_no_match(sample_request)
        assert result.selected_route is None
        assert result.fallback_used is True
        assert result.clarification is not None

    def test_handle_low_confidence(self, handler: FallbackHandler, sample_request: RoutingRequest) -> None:
        """Low confidence returns a decision with clarification."""
        decision = RoutingDecision(
            selected_route=None,
            confidence=0.35,
            rejected_routes=[
                {"route_name": "support_ticket", "score": 0.35},
                {"route_name": "policy_question", "score": 0.28},
            ],
        )
        result = handler.handle_low_confidence(sample_request, decision, processing_time_ms=50)
        assert result.clarification is not None
        assert result.fallback_used is True

    def test_handle_low_confidence_no_rejected(self, handler: FallbackHandler, sample_request: RoutingRequest) -> None:
        """Low confidence with no rejected routes produces a rephrase suggestion."""
        decision = RoutingDecision(
            selected_route=None,
            confidence=0.15,
            rejected_routes=[],
        )
        result = handler.handle_low_confidence(sample_request, decision, processing_time_ms=30)
        assert result.clarification is not None
        assert "rephrasing" in result.clarification.lower()

    def test_handle_policy_block(self, handler: FallbackHandler, sample_request: RoutingRequest) -> None:
        """Policy block clears the selected route and sets denial clarification."""
        decision = RoutingDecision(
            selected_route="refund_request",
            confidence=0.9,
            rejected_routes=[],
        )
        policy_result = PolicyCheck(
            allowed=False,
            reason="Missing permissions: billing.write",
            required_action=None,
            missing_permissions=["billing.write"],
        )
        result = handler.handle_policy_block(sample_request, decision, policy_result, processing_time_ms=40)
        assert result.selected_route is None
        assert result.fallback_used is True
        assert result.policy_check is not None
        assert result.clarification is not None
        assert "denied" in result.clarification.lower()

    def test_generate_clarification_with_routes(self, handler: FallbackHandler) -> None:
        """Clarification mentions candidate routes when available."""
        rejected = [
            {"route_name": "support_ticket", "score": 0.4},
            {"route_name": "policy_question", "score": 0.3},
        ]
        prompt = handler._generate_clarification("test query", rejected)
        assert "support_ticket" in prompt
        assert "policy_question" in prompt
