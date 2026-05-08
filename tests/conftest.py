"""Shared test fixtures for SemanticRouter tests."""

import pytest

from semantic_router.models.route import Route
from semantic_router.routing.registry import RouteRegistry


@pytest.fixture
def sample_routes() -> list[Route]:
    """Provide a list of sample routes for testing."""
    return [
        Route(
            name="invoice_lookup",
            description="Look up invoice details, billing history, or payment status",
            tool_name="invoice_lookup",
            confidence_threshold=0.7,
            required_permissions=["billing.read"],
            fallback_route="support_ticket",
        ),
        Route(
            name="support_ticket",
            description="Create a support ticket, report an issue, or get help",
            tool_name="support_ticket",
            confidence_threshold=0.6,
            required_permissions=["support.read"],
            fallback_route=None,
        ),
        Route(
            name="refund_request",
            description="Request a refund, return a product, or cancel an order",
            tool_name="refund_request",
            confidence_threshold=0.8,
            required_permissions=["billing.write", "finance.approve"],
            fallback_route="support_ticket",
        ),
        Route(
            name="policy_question",
            description="Ask about company policies, terms of service, or privacy policy",
            tool_name="policy_question",
            confidence_threshold=0.6,
            required_permissions=[],
            fallback_route=None,
        ),
        Route(
            name="sales_lead",
            description="Inquire about products, pricing, or schedule a demo",
            tool_name="sales_lead",
            confidence_threshold=0.65,
            required_permissions=["sales.read"],
            fallback_route=None,
        ),
    ]


@pytest.fixture
def populated_registry(sample_routes: list[Route]) -> RouteRegistry:
    """Provide a route registry populated with sample routes."""
    registry = RouteRegistry()
    for route in sample_routes:
        registry.register_route(route)
    return registry
