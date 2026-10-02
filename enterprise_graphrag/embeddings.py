from __future__ import annotations

import hashlib
import math
import re

import httpx


class Embedder:
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashEmbedder(Embedder):
    """Deterministic offline embeddings for CI and local demos."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in re.findall(r"[A-Za-z0-9_]{2,}", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign * (0.5 + digest[5] / 255.0)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(text) for text in texts]


class OpenAICompatibleEmbedder(Embedder):
    """Embedding adapter for vLLM or another OpenAI-compatible server."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        dimension: int,
    ) -> None:
        if not base_url or not model:
            raise ValueError(
                "EMBEDDING_BASE_URL and EMBEDDING_MODEL are required"
            )
        self.base_url = base_url.rstrip("/") + "/v1"
        self.api_key = api_key
        self.model = model
        if dimension <= 0:
            raise ValueError(
                "embedding dimension must be greater than zero"
            )
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts},
            timeout=120,
        )
        response.raise_for_status()
        items = sorted(
            response.json()["data"],
            key=lambda item: item["index"],
        )
        vectors = [item["embedding"] for item in items]
        if vectors:
            actual_dimension = len(vectors[0])
            if actual_dimension != self.dimension:
                raise ValueError(
                    "Embedding dimension mismatch: "
                    f"configured={self.dimension}, actual={actual_dimension}"
                )
            if any(
                len(vector) != self.dimension
                for vector in vectors
            ):
                raise ValueError(
                    "Embedding response contains inconsistent vector dimensions"
                )
        return vectors


def build_embedder(settings) -> Embedder:
    if settings.embedding_base_url and settings.embedding_model:
        return OpenAICompatibleEmbedder(
            settings.embedding_base_url,
            settings.embedding_api_key,
            settings.embedding_model,
            settings.embedding_dimension,
        )
    return HashEmbedder(settings.embedding_dimension)
