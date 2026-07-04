"""Domain models used across the entire application.

These are strongly typed data structures that replace raw dictionaries
in cross-module communication.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Metadata:
    """Metadata attached to a chunk or document."""

    document_id: str = ""
    document_name: str = ""
    document_hash: str = ""
    page: int | None = None
    heading: str = ""
    language: str = ""
    chunk_id: str = ""
    created_time: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_time: str = ""
    tags: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)


@dataclass
class DocumentPage:
    """A single page or section of a document."""

    text: str
    page_number: int
    metadata: dict = field(default_factory=dict)


@dataclass
class Document:
    """A loaded document with pages and metadata."""

    name: str
    path: str
    pages: list[DocumentPage] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    document_id: str = ""
    document_hash: str = ""
    version: int = 1


@dataclass
class Chunk:
    """A text chunk produced by a chunking strategy."""

    text: str
    source: str
    page: int | None = None
    heading: str = ""
    chunk_id: str = ""
    metadata: Metadata = field(default_factory=Metadata)


@dataclass
class Embedding:
    """An embedding vector associated with a chunk."""

    chunk_id: str
    vector: list[float] = field(default_factory=list)
    model_name: str = ""


@dataclass
class Query:
    """A user query with optional history."""

    question: str
    history: list[dict] = field(default_factory=list)
    top_k: int = 5
    rerank: bool = True


@dataclass
class Citation:
    """A source citation for a generated answer."""

    source: str
    page: int | None = None
    heading: str = ""
    relevance_score: float = 0.0


@dataclass
class Answer:
    """A generated answer with citations."""

    text: str
    sources: list[Citation] = field(default_factory=list)
    raw_context: list[Chunk] = field(default_factory=list)
