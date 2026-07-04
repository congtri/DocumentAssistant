from backend.chunking.heading_splitter import heading_splitter, Chunk
from backend.chunking.splitter import recursive_splitter
from backend.document.pdf_loader import Document
from backend.utils.settings import settings
from backend.utils.logger import logger


def chunk_document(document: Document) -> list[Chunk]:
    method = settings.chunking.get("method", "heading")
    all_chunks = []

    for page in document.pages:
        if method == "heading":
            chunks = heading_splitter.split(page.text, source=document.name, page=page.page_number)
        else:
            chunks = recursive_splitter.split(page.text, source=document.name, page=page.page_number)
        all_chunks.extend(chunks)

    logger.info(f"Chunked {document.name}: {len(all_chunks)} chunks")
    return all_chunks
