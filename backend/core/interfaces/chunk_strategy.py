from abc import ABC, abstractmethod

from backend.domain.models import Chunk, Document


class ChunkStrategy(ABC):
    """Interface for text chunking strategies."""

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks."""
        ...
