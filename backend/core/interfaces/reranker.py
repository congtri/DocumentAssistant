from abc import ABC, abstractmethod

from backend.domain.models import Chunk


class Reranker(ABC):
    """Interface for reranking retrieved results."""

    @abstractmethod
    def rerank(self, query: str, results: list[tuple[Chunk, float]], top_k: int = 3) -> list[tuple[Chunk, float]]:
        """Rerank results by relevance to query."""
        ...
