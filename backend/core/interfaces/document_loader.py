from abc import ABC, abstractmethod
from pathlib import Path

from backend.domain.models import Document


class DocumentLoader(ABC):
    """Interface for loading documents from various file formats."""

    @abstractmethod
    def load(self, file_path: Path) -> Document:
        """Load a document from the given file path."""
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return list of supported file extensions (e.g., ['.pdf'])."""
        ...
