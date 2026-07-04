import math

from rank_bm25 import BM25Okapi

from backend.chunking.heading_splitter import Chunk
from backend.utils.logger import logger


class BM25Store:
    def __init__(self):
        self.bm25: BM25Okapi | None = None
        self.chunks: list[Chunk] = []

    def build_index(self, chunks: list[Chunk]) -> None:
        if not chunks:
            logger.warning("No chunks to index for BM25")
            return

        self.chunks = chunks
        tokenized = [self._tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(tokenized)
        logger.info(f"Built BM25 index with {len(chunks)} documents")

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if self.bm25 is None or not self.chunks:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.chunks[idx], float(scores[idx])))

        return results

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()


bm25_store = BM25Store()
