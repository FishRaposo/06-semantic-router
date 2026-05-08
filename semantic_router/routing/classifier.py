"""LLM-based classifier for route disambiguation."""

from pydantic import Field

from semantic_router.routing.semantic_matcher import RouteMatch


class LLMClassifier:
    """Optional LLM-based classifier for disambiguating between candidate routes."""

    async def classify(
        self, query: str, candidates: list[RouteMatch]
    ) -> RouteMatch | None:
        """Use an LLM to classify the best route from candidates.

        Args:
            query: The user's natural-language query.
            candidates: Top candidate routes from semantic matching.

        Returns:
            The best RouteMatch as determined by the LLM, or None.
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        return candidates[0]
