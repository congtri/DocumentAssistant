"""Metadata manager for attaching metadata to chunks."""

import hashlib
from datetime import datetime

from backend.domain.models import Chunk, Document, Metadata
from backend.core.logger import logger


class MetadataManager:
    """Attaches and manages metadata for documents and chunks."""

    def attach_document_metadata(self, document: Document) -> Document:
        """Generate document ID and hash if not already set."""
        if not document.document_hash:
            content = "".join(page.text for page in document.pages)
            document.document_hash = hashlib.sha256(content.encode()).hexdigest()
        if not document.document_id:
            document.document_id = f"doc:{document.document_hash[:12]}"
        return document

    def attach_chunk_metadata(self, chunks: list[Chunk], document: Document) -> list[Chunk]:
        """Attach rich metadata to each chunk."""
        now = datetime.now().isoformat()
        for i, chunk in enumerate(chunks):
            chunk.metadata = Metadata(
                document_id=document.document_id,
                document_name=document.name,
                document_hash=document.document_hash,
                page=chunk.page,
                heading=chunk.heading,
                chunk_id=chunk.chunk_id or f"{document.name}:c{i}",
                created_time=now,
            )
            if not chunk.chunk_id:
                chunk.chunk_id = chunk.metadata.chunk_id
        logger.info(f"Attached metadata to {len(chunks)} chunks from {document.name}")
        return chunks

    def compute_hash(self, content: str) -> str:
        """Compute SHA256 hash for content."""
        return hashlib.sha256(content.encode()).hexdigest()


metadata_manager = MetadataManager()
