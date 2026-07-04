from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class StorageProvider(ABC):
    """Interface for persisting data (chunks, embeddings, metadata)."""

    @abstractmethod
    def save(self, key: str, data: Any) -> None:
        """Save data under the given key."""
        ...

    @abstractmethod
    def load(self, key: str) -> Any | None:
        """Load data by key. Returns None if not found."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check whether data exists for the given key."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete data by key."""
        ...
