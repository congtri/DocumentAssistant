"""Pipeline context carrying data between stages."""

from dataclasses import dataclass, field
from typing import Any

from backend.domain.models import Document, Chunk


@dataclass
class PipelineContext:
    """Mutable context passed through pipeline stages."""

    documents: list[Document] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def add_error(self, error: str) -> None:
        self.errors.append(error)
