"""Fallback handling for low confidence, no match, and policy block scenarios."""

from semantic_router.models.decision import PolicyCheck, RoutingDecision
from semantic_router.models.request import RoutingRequest


class FallbackHandler:
    """Handles routing fallbacks for various failure scenarios."""

    def handle_no_match(self, request: RoutingRequest) -> RoutingDecision:
        """Handle the case where no routes are registered.

        Args:
            request: The original routing request.

        Returns:
            A RoutingDecision indicating no match was possible.
        """
        return RoutingDecision(
            selected_route=None,
            confidence=0.0,
            rejected_routes=[],
            policy_check=PolicyCheck(allowed=False, reason="No routes registered"),
            fallback_used=True,
            clarification="No tools are currently available. Please try again later.",
        )

    def handle_low_confidence(
        self,
        request: RoutingRequest,
        decision: RoutingDecision,
        processing_time_ms: int,
    ) -> RoutingDecision:
        """Handle the case where confidence is too low to select a route.

        Args:
            request: The original routing request.
            decision: The initial routing decision with low confidence.
            processing_time_ms: Time taken for processing.

        Returns:
            A RoutingDecision with a clarification prompt.
        """
        clarification = self._generate_clarification(request.query, decision.rejected_routes)
        decision.clarification = clarification
        decision.fallback_used = True
        return decision

    def handle_policy_block(
        self,
        request: RoutingRequest,
        decision: RoutingDecision,
        policy_result: PolicyCheck,
        processing_time_ms: int,
    ) -> RoutingDecision:
        """Handle the case where policy blocks the selected route.

        Args:
            request: The original routing request.
            decision: The routing decision with a policy-blocked route.
            policy_result: The policy evaluation result.
            processing_time_ms: Time taken for processing.

        Returns:
            A RoutingDecision indicating the policy block.
        """
        decision.selected_route = None
        decision.fallback_used = True
        decision.policy_check = policy_result
        decision.clarification = (
            f"Access denied: {policy_result.reason}. "
            f"Please contact an administrator if you believe this is an error."
        )
        return decision

    def _generate_clarification(
        self, query: str, rejected_routes: list[dict[str, str | float]]
    ) -> str:
        """Generate a clarification prompt for ambiguous queries.

        Args:
            query: The original user query.
            rejected_routes: Routes that were considered but not confidently selected.

        Returns:
            A clarification prompt string.
        """
        if not rejected_routes:
            return (
                f"I couldn't find a matching tool for your request: '{query}'. "
                "Could you try rephrasing your question?"
            )

        route_names = [str(r.get("route_name", "")) for r in rejected_routes[:3]]
        options = ", ".join(route_names)
        return (
            f"I'm not confident about the best tool for your request. "
            f"It might relate to: {options}. Could you clarify what you need?"
        )
