from backend.core.interfaces.reranker import Reranker as RerankerInterface
from backend.core.logger import logger
from backend.domain.models import Chunk
from backend.embedding.embedding_service import embedding_service

import numpy as np


class EmbeddingReranker(RerankerInterface):
    """Reranker using embedding similarity as a proxy for cross-encoder scoring."""

    def rerank(self, query: str, results: list[tuple[Chunk, float]], top_k: int = 3) -> list[tuple[Chunk, float]]:
        if not results:
            return []

        query_embedding = embedding_service.embed_query(query)
        texts = [chunk.text for chunk, _ in results]
        text_embeddings = embedding_service.embed_texts(texts)

        scores = np.dot(text_embeddings, query_embedding)

        reranked = []
        for i, (chunk, original_score) in enumerate(results):
            combined = 0.3 * original_score + 0.7 * float(scores[i])
            reranked.append((chunk, combined))

        reranked.sort(key=lambda x: x[1], reverse=True)
        result = reranked[:top_k]
        logger.info(f"Reranked to top {len(result)} results")
        return result


reranker = EmbeddingReranker()
