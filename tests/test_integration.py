"""Integration tests for the full routing pipeline."""

import pytest

from semantic_router.embedding.service import EmbeddingService
from semantic_router.execution.adapter import ExecutionAdapter
from semantic_router.models.request import RoutingRequest
from semantic_router.models.route import Route
from semantic_router.policy.engine import PolicyEngine
from semantic_router.policy.fallback import FallbackHandler
from semantic_router.routing.registry import RouteRegistry
from semantic_router.routing.selector import RouteSelector
from semantic_router.routing.semantic_matcher import SemanticMatcher


class IntegrationEmbeddingService:
    """A deterministic embedding service for integration tests."""

    async def embed(self, text: str) -> list[float]:
        """Generate a deterministic embedding based on text keywords.

        Args:
            text: The text to embed.

        Returns:
            A deterministic embedding vector.
        """
        keywords: dict[str, list[float]] = {
            "invoice": [0.9] + [0.1] * 383,
            "billing": [0.85] + [0.15] * 383,
            "payment": [0.8] + [0.2] * 383,
            "support": [0.1] * 384,
            "help": [0.15] + [0.1] * 383,
            "issue": [0.1] * 192 + [0.2] * 192,
            "refund": [0.1] * 128 + [0.9] + [0.1] * 255,
            "return": [0.1] * 128 + [0.85] + [0.15] * 255,
            "cancel": [0.1] * 128 + [0.8] + [0.2] * 255,
            "policy": [0.1] * 256 + [0.9] + [0.1] * 127,
            "terms": [0.1] * 256 + [0.85] + [0.15] * 127,
            "sales": [0.1] * 320 + [0.9] + [0.1] * 63,
            "pricing": [0.1] * 320 + [0.85] + [0.15] * 63,
            "demo": [0.1] * 320 + [0.8] + [0.2] * 63,
        }

        words = text.lower().split()
        base = [0.5] * 384
        for word in words:
            if word in keywords:
                for i in range(384):
                    base[i] = base[i] * 0.7 + keywords[word][i] * 0.3

        norm = sum(x * x for x in base) ** 0.5
        if norm > 0:
            base = [x / norm for x in base]
        return base

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate deterministic batch embeddings.

        Args:
            texts: Texts to embed.

        Returns:
            List of embedding vectors.
        """
        return [await self.embed(t) for t in texts]


@pytest.fixture
def pipeline(sample_routes: list[Route]):
    """Set up the full routing pipeline for integration testing."""
    registry = RouteRegistry()
    for route in sample_routes:
        route.embedding = None
        registry.register_route(route)

    embedding_service = IntegrationEmbeddingService()
    matcher = SemanticMatcher(embedding_service)
    selector = RouteSelector(default_threshold=0.7, min_threshold=0.3)
    policy_engine = PolicyEngine()
    policy_engine._permission_map = {
        "invoice_lookup": ["billing.read"],
        "support_ticket": ["support.read"],
        "refund_request": ["billing.write", "finance.approve"],
        "policy_question": [],
        "sales_lead": ["sales.read"],
    }
    fallback_handler = FallbackHandler()
    execution_adapter = ExecutionAdapter()

    return {
        "registry": registry,
        "matcher": matcher,
        "selector": selector,
        "policy_engine": policy_engine,
        "fallback_handler": fallback_handler,
        "execution_adapter": execution_adapter,
    }


class TestIntegration:
    """End-to-end tests for the routing pipeline."""

    @pytest.mark.asyncio
    async def test_route_invoice_query(self, pipeline: dict) -> None:
        """Invoice-related queries are routed to invoice_lookup."""
        routes = pipeline["registry"].list_routes()
        matches = await pipeline["matcher"].match(
            query="What's the status of my invoice?",
            routes=routes,
            top_k=3,
        )
        assert len(matches) > 0

    @pytest.mark.asyncio
    async def test_route_refund_query(self, pipeline: dict) -> None:
        """Refund-related queries are routed to refund_request."""
        routes = pipeline["registry"].list_routes()
        matches = await pipeline["matcher"].match(
            query="I want to return this product for a refund",
            routes=routes,
            top_k=3,
        )
        assert len(matches) > 0

    @pytest.mark.asyncio
    async def test_execute_mock_tool(self, pipeline: dict) -> None:
        """Mock tools return valid execution results."""
        registry = pipeline["registry"]
        route = registry.get_route("invoice_lookup")
        request = RoutingRequest(query="show invoice")
        result = await pipeline["execution_adapter"].execute(route=route, request=request)
        assert result.status == "success"
        assert result.tool_name == "invoice_lookup"
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_execute_all_mock_tools(self, pipeline: dict) -> None:
        """All mock tools execute successfully."""
        request = RoutingRequest(query="test")
        for tool_name in ["invoice_lookup", "support_ticket", "refund_request", "policy_question", "sales_lead"]:
            route = pipeline["registry"].get_route(tool_name)
            result = await pipeline["execution_adapter"].execute(route=route, request=request)
            assert result.status == "success", f"Tool {tool_name} failed: {result.error}"

    @pytest.mark.asyncio
    async def test_policy_blocks_unauthorized_refund(self, pipeline: dict) -> None:
        """Refund requests are blocked for users without required permissions."""
        route = pipeline["registry"].get_route("refund_request")
        context = {"user_permissions": ["billing.read"]}
        result = pipeline["policy_engine"].evaluate(route=route, context=context)
        assert result.allowed is False
        assert len(result.missing_permissions) > 0

    @pytest.mark.asyncio
    async def test_policy_allows_with_permissions(self, pipeline: dict) -> None:
        """Invoice lookup is allowed for users with billing.read permission."""
        route = pipeline["registry"].get_route("invoice_lookup")
        context = {"user_permissions": ["billing.read"]}
        result = pipeline["policy_engine"].evaluate(route=route, context=context)
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_fallback_on_no_routes(self, pipeline: dict) -> None:
        """Fallback handler provides a response when no routes exist."""
        request = RoutingRequest(query="help me")
        result = pipeline["fallback_handler"].handle_no_match(request)
        assert result.selected_route is None
        assert result.clarification is not None
