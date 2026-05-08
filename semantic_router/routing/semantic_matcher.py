"""Semantic matching between queries and routes using embeddings."""

import numpy as np
from pydantic import BaseModel, Field

from semantic_router.models.route import Route


class RouteMatch(BaseModel):
    """A route match result with confidence score."""

    route_name: str = Field(..., description="Name of the matched route")
    score: float = Field(..., description="Cosine similarity score")
    description: str = Field(..., description="Description of the matched route")


class SemanticMatcher:
    """Matches user queries to routes using embedding cosine similarity."""

    def __init__(self, embedding_service: "EmbeddingService") -> None:
        """Initialize the semantic matcher with an embedding service.

        Args:
            embedding_service: Service for generating text embeddings.
        """
        self._embedding_service = embedding_service

    async def match(
        self, query: str, routes: list[Route], top_k: int = 5
    ) -> list[RouteMatch]:
        """Find the best-matching routes for a user query.

        Args:
            query: The user's natural-language query.
            routes: Candidate routes to match against.
            top_k: Maximum number of matches to return.

        Returns:
            List of RouteMatch objects sorted by score descending.
        """
        if not routes:
            return []

        query_embedding = await self._embedding_service.embed(query)

        route_embeddings: list[np.ndarray] = []
        route_names: list[str] = []
        route_descriptions: list[str] = []

        for route in routes:
            if route.embedding is not None:
                route_embeddings.append(np.array(route.embedding))
            else:
                route_emb = await self._embedding_service.embed(route.description)
                route_embeddings.append(np.array(route_emb))
            route_names.append(route.name)
            route_descriptions.append(route.description)

        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        scores: list[tuple[int, float]] = []
        for idx, route_emb in enumerate(route_embeddings):
            route_norm = np.linalg.norm(route_emb)
            if route_norm == 0:
                scores.append((idx, 0.0))
                continue
            similarity = float(np.dot(query_vec, route_emb) / (query_norm * route_norm))
            scores.append((idx, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)

        matches: list[RouteMatch] = []
        for idx, score in scores[:top_k]:
            matches.append(
                RouteMatch(
                    route_name=route_names[idx],
                    score=score,
                    description=route_descriptions[idx],
                )
            )

        return matches
