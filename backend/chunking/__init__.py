from backend.chunking.heading_splitter import heading_splitter
from backend.chunking.splitter import recursive_splitter
from backend.core.config import config
from backend.core.logger import logger
from backend.domain.models import Chunk, Document


def chunk_document(document: Document) -> list[Chunk]:
    method = config.chunking.get("method", "heading")

    if method == "heading":
        all_chunks = heading_splitter.chunk(document)
    else:
        all_chunks = recursive_splitter.chunk(document)

    logger.info(f"Chunked {document.name}: {len(all_chunks)} chunks")
    return all_chunks
