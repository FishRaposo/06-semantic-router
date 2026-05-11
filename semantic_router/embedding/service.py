"""Embedding service supporting OpenAI and sentence-transformers."""

import asyncio
import hashlib
import logging
from typing import Any

import numpy as np

from semantic_router.config import settings

logger = logging.getLogger(__name__)

_fallback_counter: int = 0


def get_fallback_count() -> int:
    """Return the number of times the fallback embedding has been used.

    Returns:
        The global fallback usage count.
    """
    return _fallback_counter


def reset_fallback_count() -> None:
    """Reset the fallback counter to zero."""
    global _fallback_counter
    _fallback_counter = 0


class EmbeddingService:
    """Generates text embeddings using OpenAI or sentence-transformers backends."""

    def __init__(self) -> None:
        """Initialize the embedding service based on configured provider."""
        self._provider = settings.embedding_provider
        self._model_name: str = ""
        self._client: Any = None
        self._st_model: Any = None
        self._cache: dict[str, list[float]] = {}

        if self._provider == "openai":
            self._model_name = settings.openai_embedding_model
        else:
            self._model_name = settings.sentence_transformers_model

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text input.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        cache_key = self._cache_key(text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self._provider == "openai":
            embedding = await self._embed_openai(text)
        else:
            embedding = await self._embed_sentence_transformers(text)

        self._cache[cache_key] = embedding
        return embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple text inputs.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []
        results: list[list[float]] = [ [] for _ in texts]

        for idx, text in enumerate(texts):
            cache_key = self._cache_key(text)
            if cache_key in self._cache:
                results[idx] = self._cache[cache_key]
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        if uncached_texts:
            if self._provider == "openai":
                batch_embeddings = await self._embed_batch_openai(uncached_texts)
            else:
                batch_embeddings = await self._embed_batch_sentence_transformers(uncached_texts)

            for i, idx in enumerate(uncached_indices):
                results[idx] = batch_embeddings[i]
                cache_key = self._cache_key(uncached_texts[i])
                self._cache[cache_key] = batch_embeddings[i]

        return results

    async def _embed_openai(self, text: str) -> list[float]:
        """Embed text using the OpenAI API.

        Args:
            text: The text to embed.

        Returns:
            Embedding vector from OpenAI.
        """
        try:
            from openai import AsyncOpenAI

            if self._client is None:
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)

            response = await self._client.embeddings.create(
                input=[text],
                model=self._model_name,
            )
            return response.data[0].embedding
        except Exception:
            return self._fallback_embedding(text)

    async def _embed_sentence_transformers(self, text: str) -> list[float]:
        """Embed text using sentence-transformers.

        Args:
            text: The text to embed.

        Returns:
            Embedding vector from sentence-transformers.
        """
        try:
            from sentence_transformers import SentenceTransformer

            if self._st_model is None:
                self._st_model = SentenceTransformer(self._model_name)

            embedding = await asyncio.to_thread(self._st_model.encode, text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception:
            return self._fallback_embedding(text)

    async def _embed_batch_openai(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts using the OpenAI API.

        Args:
            texts: Texts to embed.

        Returns:
            List of embedding vectors.
        """
        try:
            from openai import AsyncOpenAI

            if self._client is None:
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)

            response = await self._client.embeddings.create(
                input=texts,
                model=self._model_name,
            )
            return [item.embedding for item in response.data]
        except Exception:
            return [self._fallback_embedding(t) for t in texts]

    async def _embed_batch_sentence_transformers(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts using sentence-transformers.

        Args:
            texts: Texts to embed.

        Returns:
            List of embedding vectors.
        """
        try:
            from sentence_transformers import SentenceTransformer

            if self._st_model is None:
                self._st_model = SentenceTransformer(self._model_name)

            embeddings = await asyncio.to_thread(self._st_model.encode, texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception:
            return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-embedding for fallback when providers are unavailable.

        Args:
            text: The text to hash into an embedding.

        Returns:
            A deterministic 384-dimensional pseudo-embedding vector.
        """
        global _fallback_counter
        logger.warning("OpenAI embedding failed, using hash-based fallback")
        _fallback_counter += 1
        dim = 384
        chunks = [text[i:i+16] for i in range(0, max(len(text), 16), 16)]
        embedding: list[float] = []
        for i in range(dim):
            chunk = chunks[i % len(chunks)]
            hash_val = hashlib.md5(f"{chunk}:{i}".encode()).hexdigest()
            val = int(hash_val[:8], 16) / 0xFFFFFFFF
            embedding.append(val)
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def _cache_key(self, text: str) -> str:
        """Generate a cache key for a text input.

        Args:
            text: The text to generate a key for.

        Returns:
            A hash-based cache key string.
        """
        return hashlib.sha256(f"{self._provider}:{self._model_name}:{text}".encode()).hexdigest()
