import json
from pathlib import Path

import numpy as np
import faiss

from backend.core.interfaces.retriever import Retriever
from backend.core.logger import logger
from backend.core.config import config
from backend.domain.models import Chunk
from backend.embedding.embedding_service import embedding_service


class FAISSStore(Retriever):
    def __init__(self):
        self._dimension = config.embedding.get("dimension", 384)
        self.index: faiss.IndexFlatIP | None = None
        self.chunks: list[Chunk] = []
        self._index_path = config.get_path(config.data.get("indexes_dir", "data/indexes")) / "faiss.index"
        self._meta_path = config.get_path(config.data.get("indexes_dir", "data/indexes")) / "chunks.json"

    def build_index(self, chunks: list[Chunk]) -> None:
        if not chunks:
            logger.warning("No chunks to index")
            return

        texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_texts(texts)

        self.index = faiss.IndexFlatIP(self._dimension)
        self.index.add(embeddings)
        self.chunks = chunks

        logger.info(f"Built FAISS index with {len(chunks)} vectors")

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = embedding_service.embed_query(query)
        query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))

        return results

    def save(self) -> None:
        if self.index is None:
            return

        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self._index_path))

        chunks_data = [
            {
                "text": c.text,
                "source": c.source,
                "page": c.page,
                "heading": c.heading,
                "chunk_id": c.chunk_id,
            }
            for c in self.chunks
        ]
        self._meta_path.write_text(json.dumps(chunks_data, ensure_ascii=False, indent=2))
        logger.info(f"Saved FAISS index: {self.index.ntotal} vectors")

    def load(self) -> bool:
        if not self._index_path.exists() or not self._meta_path.exists():
            return False

        self.index = faiss.read_index(str(self._index_path))
        chunks_data = json.loads(self._meta_path.read_text())
        self.chunks = [
            Chunk(
                text=c["text"],
                source=c["source"],
                page=c.get("page"),
                heading=c.get("heading", ""),
                chunk_id=c.get("chunk_id", ""),
            )
            for c in chunks_data
        ]
        logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
        return True


faiss_store = FAISSStore()
