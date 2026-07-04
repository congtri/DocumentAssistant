from abc import ABC, abstractmethod

from backend.domain.models import Chunk


class Retriever(ABC):
    """Interface for retrieving relevant chunks."""

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Search for chunks relevant to the query. Returns (chunk, score) pairs."""
        ...

    @abstractmethod
    def build_index(self, chunks: list[Chunk]) -> None:
        """Build search index from chunks."""
        ...
