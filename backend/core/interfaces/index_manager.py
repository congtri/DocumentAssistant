from abc import ABC, abstractmethod

from backend.domain.models import Chunk


class IndexManager(ABC):
    """Interface for managing search indexes."""

    @abstractmethod
    def build(self, chunks: list[Chunk]) -> None:
        """Build indexes from chunks."""
        ...

    @abstractmethod
    def delete(self) -> None:
        """Delete all indexes."""
        ...

    @abstractmethod
    def exists(self) -> bool:
        """Check if indexes exist."""
        ...

    @abstractmethod
    def load(self) -> bool:
        """Load indexes from storage. Returns True if successful."""
        ...
