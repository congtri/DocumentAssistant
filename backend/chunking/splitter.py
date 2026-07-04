from dataclasses import dataclass, field

from backend.utils.logger import logger
from backend.utils.settings import settings


@dataclass
class Chunk:
    text: str
    source: str
    page: int | None = None
    heading: str = ""
    chunk_id: str = ""
    metadata: dict = field(default_factory=dict)


class RecursiveSplitter:
    def __init__(self):
        config = settings.chunking
        self.chunk_size = config.get("chunk_size", 512)
        self.chunk_overlap = config.get("chunk_overlap", 50)
        self.min_chunk_size = config.get("min_chunk_size", 100)

    def split(self, text: str, source: str, page: int | None = None) -> list[Chunk]:
        if not text.strip():
            return []

        separators = ["\n\n", "\n", ". ", " "]
        pieces = self._recursive_split(text, separators)

        chunks = []
        for i, piece in enumerate(pieces):
            if len(piece.strip()) >= self.min_chunk_size:
                chunks.append(Chunk(
                    text=piece.strip(),
                    source=source,
                    page=page,
                    chunk_id=f"{source}:p{page or 0}:c{i}",
                ))

        logger.info(f"Recursive split: {len(chunks)} chunks from {source}")
        return chunks

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # Hard split by character count
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunks.append(text[i : i + self.chunk_size])
            return chunks

        sep = separators[0]
        parts = text.split(sep)
        chunks = []
        current = ""

        for part in parts:
            candidate = current + sep + part if current else part
            if len(candidate) > self.chunk_size and current:
                chunks.append(current)
                # Overlap: keep end of previous chunk
                overlap_text = current[-self.chunk_overlap :] if self.chunk_overlap else ""
                current = overlap_text + part
            else:
                current = candidate

        if current:
            chunks.append(current)

        # Recursively split any chunks that are still too large
        result = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                result.extend(self._recursive_split(chunk, separators[1:]))
            else:
                result.append(chunk)

        return result


recursive_splitter = RecursiveSplitter()
