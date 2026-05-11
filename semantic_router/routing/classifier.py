"""LLM-based classifier for route disambiguation."""

from openai import AsyncOpenAI

from semantic_router.config import settings
from semantic_router.routing.semantic_matcher import RouteMatch


class LLMClassifier:
    """Optional LLM-based classifier for disambiguating between candidate routes."""

    def __init__(self, model: str | None = None) -> None:
        """Initialize the LLM classifier.

        Args:
            model: The OpenAI chat model to use. Defaults to settings.openai_chat_model.
        """
        self._model = model or settings.openai_chat_model
        self._client: AsyncOpenAI | None = None

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

        if not settings.openai_api_key:
            return candidates[0]

        try:
            if self._client is None:
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)

            candidate_lines = "\n".join(
                f"- {c.route_name}: {c.description}" for c in candidates
            )
            prompt = (
                "You are a routing classifier. Given a user query and a list of possible routes, "
                "select the single most appropriate route.\n\n"
                f"User query: \"{query}\"\n\n"
                "Available routes:\n"
                f"{candidate_lines}\n\n"
                "Respond with ONLY the exact route name, nothing else."
            )

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=50,
            )

            selected_name = response.choices[0].message.content
            if selected_name:
                selected_name = selected_name.strip()
                for candidate in candidates:
                    if candidate.route_name == selected_name:
                        return candidate

            return candidates[0]

        except Exception:
            return candidates[0]
