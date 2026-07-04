from abc import ABC, abstractmethod

import numpy as np


class EmbeddingProvider(ABC):
    """Interface for generating vector embeddings."""

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of texts into vectors."""
        ...

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query into a vector."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        ...
