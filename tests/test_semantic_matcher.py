"""Tests for the SemanticMatcher."""

import pytest

from semantic_router.embedding.service import EmbeddingService
from semantic_router.models.route import Route
from semantic_router.routing.semantic_matcher import RouteMatch, SemanticMatcher


class MockEmbeddingService:
    """A mock embedding service that returns deterministic embeddings for testing."""

    async def embed(self, text: str) -> list[float]:
        """Generate a deterministic embedding based on text content.

        Args:
            text: The text to embed.

        Returns:
            A deterministic embedding vector.
        """
        base = hash(text) % 1000 / 1000.0
        return [base + i * 0.001 for i in range(384)]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate deterministic batch embeddings.

        Args:
            texts: Texts to embed.

        Returns:
            List of embedding vectors.
        """
        return [await self.embed(t) for t in texts]


@pytest.fixture
def matcher() -> SemanticMatcher:
    """Provide a semantic matcher with a mock embedding service."""
    return SemanticMatcher(embedding_service=MockEmbeddingService())


class TestSemanticMatcher:
    """Tests for semantic matching between queries and routes."""

    @pytest.mark.asyncio
    async def test_match_returns_results(self, matcher: SemanticMatcher, sample_routes: list[Route]) -> None:
        """Matching a query returns ranked route matches."""
        matches = await matcher.match(query="show me invoice details", routes=sample_routes, top_k=3)
        assert len(matches) <= 3
        assert all(isinstance(m, RouteMatch) for m in matches)

    @pytest.mark.asyncio
    async def test_match_empty_routes(self, matcher: SemanticMatcher) -> None:
        """Matching with no routes returns empty list."""
        matches = await matcher.match(query="test", routes=[], top_k=5)
        assert matches == []

    @pytest.mark.asyncio
    async def test_match_scores_sorted_desc(self, matcher: SemanticMatcher, sample_routes: list[Route]) -> None:
        """Match scores are sorted in descending order."""
        matches = await matcher.match(query="look up my invoice", routes=sample_routes, top_k=5)
        scores = [m.score for m in matches]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_match_top_k_limits_results(self, matcher: SemanticMatcher, sample_routes: list[Route]) -> None:
        """Top-k parameter limits the number of returned matches."""
        matches = await matcher.match(query="test", routes=sample_routes, top_k=2)
        assert len(matches) <= 2

    @pytest.mark.asyncio
    async def test_match_with_route_embeddings(self, matcher: SemanticMatcher) -> None:
        """Matching uses pre-computed route embeddings when available."""
        routes = [
            Route(
                name="r1",
                description="route one",
                tool_name="t1",
                confidence_threshold=0.7,
                embedding=[0.5 + i * 0.001 for i in range(384)],
            ),
            Route(
                name="r2",
                description="route two",
                tool_name="t2",
                confidence_threshold=0.7,
                embedding=[0.3 + i * 0.001 for i in range(384)],
            ),
        ]
        matches = await matcher.match(query="test query", routes=routes, top_k=5)
        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_match_route_match_model(self, matcher: SemanticMatcher, sample_routes: list[Route]) -> None:
        """Each match is a valid RouteMatch with required fields."""
        matches = await matcher.match(query="help", routes=sample_routes[:1], top_k=1)
        assert len(matches) == 1
        match = matches[0]
        assert match.route_name == sample_routes[0].name
        assert 0.0 <= match.score <= 2.0
        assert match.description == sample_routes[0].description
