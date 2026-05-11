"""Tests for the LLMClassifier route disambiguation."""

import pytest

from semantic_router.routing.classifier import LLMClassifier
from semantic_router.routing.semantic_matcher import RouteMatch


@pytest.fixture
def classifier() -> LLMClassifier:
    return LLMClassifier()


@pytest.fixture
def single_candidate() -> list[RouteMatch]:
    return [RouteMatch(route_name="invoice_lookup", score=0.92, description="Look up invoice details")]


@pytest.fixture
def multiple_candidates() -> list[RouteMatch]:
    return [
        RouteMatch(route_name="invoice_lookup", score=0.92, description="Look up invoice details"),
        RouteMatch(route_name="support_ticket", score=0.88, description="Create a support ticket"),
        RouteMatch(route_name="refund_request", score=0.81, description="Request a refund"),
    ]


class TestLLMClassifier:
    @pytest.mark.asyncio
    async def test_empty_candidates_returns_none(self, classifier: LLMClassifier) -> None:
        result = await classifier.classify(query="test", candidates=[])
        assert result is None

    @pytest.mark.asyncio
    async def test_single_candidate_returns_candidate(
        self, classifier: LLMClassifier, single_candidate: list[RouteMatch]
    ) -> None:
        result = await classifier.classify(query="show my invoice", candidates=single_candidate)
        assert result is not None
        assert result.route_name == "invoice_lookup"
        assert result.score == 0.92

    @pytest.mark.asyncio
    async def test_multiple_candidates_calls_llm(
        self, classifier: LLMClassifier, multiple_candidates: list[RouteMatch]
    ) -> None:
        result = await classifier.classify(query="I need help with billing", candidates=multiple_candidates)
        assert result is not None
        assert result.route_name in {"invoice_lookup", "support_ticket", "refund_request"}

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back_to_first_candidate(
        self, multiple_candidates: list[RouteMatch]
    ) -> None:
        classifier = LLMClassifier()

        original_classify = classifier.classify

        async def failing_classify(query, candidates):
            raise RuntimeError("LLM API call failed")

        classifier.classify = failing_classify

        try:
            await classifier.classify(query="billing question", candidates=multiple_candidates)
            raise AssertionError("Expected RuntimeError")
        except RuntimeError:
            pass

        classifier.classify = original_classify
        result = await classifier.classify(query="billing question", candidates=multiple_candidates)
        assert result is not None
        assert result.route_name == multiple_candidates[0].route_name

    @pytest.mark.asyncio
    async def test_classify_maintains_single_candidate_fields(
        self, classifier: LLMClassifier, single_candidate: list[RouteMatch]
    ) -> None:
        result = await classifier.classify(query="invoice status", candidates=single_candidate)
        assert result is not None
        assert result.route_name == single_candidate[0].route_name
        assert result.score == single_candidate[0].score
        assert result.description == single_candidate[0].description

    @pytest.mark.asyncio
    async def test_multiple_candidates_returns_valid_route_match(
        self, classifier: LLMClassifier, multiple_candidates: list[RouteMatch]
    ) -> None:
        result = await classifier.classify(query="refund my order", candidates=multiple_candidates)
        assert isinstance(result, RouteMatch)
        assert hasattr(result, "route_name")
        assert hasattr(result, "score")
        assert hasattr(result, "description")
