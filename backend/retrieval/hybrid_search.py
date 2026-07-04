from backend.chunking.heading_splitter import Chunk
from backend.retrieval.faiss_store import faiss_store
from backend.retrieval.bm25_store import bm25_store
from backend.utils.logger import logger
from backend.utils.settings import settings


class HybridSearch:
    def __init__(self):
        config = settings.retrieval
        self.bm25_weight = config.get("bm25_weight", 0.4)
        self.vector_weight = config.get("vector_weight", 0.6)
        self.top_k = config.get("top_k", 5)

    def search(self, query: str, top_k: int | None = None) -> list[tuple[Chunk, float]]:
        k = top_k or self.top_k

        # Get results from both stores
        vector_results = faiss_store.search(query, top_k=k * 2)
        bm25_results = bm25_store.search(query, top_k=k * 2)

        # Normalize and combine scores
        score_map: dict[str, tuple[Chunk, float]] = {}

        # Normalize vector scores
        if vector_results:
            max_score = max(s for _, s in vector_results) or 1.0
            for chunk, score in vector_results:
                normalized = (score / max_score) * self.vector_weight
                key = chunk.chunk_id or chunk.text[:50]
                if key in score_map:
                    score_map[key] = (chunk, score_map[key][1] + normalized)
                else:
                    score_map[key] = (chunk, normalized)

        # Normalize BM25 scores
        if bm25_results:
            max_score = max(s for _, s in bm25_results) or 1.0
            for chunk, score in bm25_results:
                normalized = (score / max_score) * self.bm25_weight
                key = chunk.chunk_id or chunk.text[:50]
                if key in score_map:
                    score_map[key] = (chunk, score_map[key][1] + normalized)
                else:
                    score_map[key] = (chunk, normalized)

        # Sort by combined score
        ranked = sorted(score_map.values(), key=lambda x: x[1], reverse=True)
        results = ranked[:k]

        logger.info(f"Hybrid search: {len(results)} results for query")
        return results

    def build_indexes(self, chunks: list[Chunk]) -> None:
        faiss_store.build_index(chunks)
        bm25_store.build_index(chunks)
        logger.info(f"Built hybrid indexes with {len(chunks)} chunks")


hybrid_search = HybridSearch()
