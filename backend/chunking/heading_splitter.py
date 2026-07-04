import re

from backend.core.interfaces.chunk_strategy import ChunkStrategy
from backend.core.logger import logger
from backend.core.config import config
from backend.domain.models import Chunk, Document


class HeadingSplitter(ChunkStrategy):
    def __init__(self):
        chunking_config = config.chunking
        self.chunk_size = chunking_config.get("chunk_size", 512)
        self.min_chunk_size = chunking_config.get("min_chunk_size", 100)

    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks by headings."""
        all_chunks = []
        for page in document.pages:
            chunks = self.split(page.text, source=document.name, page=page.page_number)
            all_chunks.extend(chunks)
        return all_chunks

    def split(self, text: str, source: str, page: int | None = None) -> list[Chunk]:
        # Split by markdown headings
        sections = re.split(r"(^#{1,6}\s+.+$)", text, flags=re.MULTILINE)

        chunks = []
        current_heading = ""
        current_text = ""

        for section in sections:
            if re.match(r"^#{1,6}\s+", section):
                # Save previous section
                if current_text.strip() and len(current_text.strip()) >= self.min_chunk_size:
                    chunks.extend(self._split_large_section(current_text.strip(), source, page, current_heading))
                current_heading = section.strip()
                current_text = ""
            else:
                current_text += section

        # Handle last section
        if current_text.strip() and len(current_text.strip()) >= self.min_chunk_size:
            chunks.extend(self._split_large_section(current_text.strip(), source, page, current_heading))

        # Assign chunk IDs
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = f"{source}:p{page or 0}:c{i}"

        logger.info(f"Split into {len(chunks)} chunks from {source}")
        return chunks

    def _split_large_section(self, text: str, source: str, page: int | None, heading: str) -> list[Chunk]:
        if len(text) <= self.chunk_size:
            return [Chunk(text=text, source=source, page=page, heading=heading)]

        chunks = []
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) > self.chunk_size and current:
                chunks.append(Chunk(text=current.strip(), source=source, page=page, heading=heading))
                current = sentence
            else:
                current += " " + sentence if current else sentence

        if current.strip():
            chunks.append(Chunk(text=current.strip(), source=source, page=page, heading=heading))

        return chunks


heading_splitter = HeadingSplitter()
