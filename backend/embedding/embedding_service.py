from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.core.interfaces.embedding_provider import EmbeddingProvider
from backend.core.logger import logger
from backend.core.config import config


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self):
        embedding_config = config.embedding
        self.model_name = embedding_config.get("model_name", "all-MiniLM-L6-v2")
        self._dimension = embedding_config.get("dimension", 384)
        self.batch_size = embedding_config.get("batch_size", 32)
        self._model = None

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            cache_folder = str(config.get_path(config.embedding.get("model_path", "models/embeddings")))
            self._model = SentenceTransformer(self.model_name, cache_folder=cache_folder)
        return self._model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )
        return np.array(embedding, dtype=np.float32)[0]


embedding_service = SentenceTransformerProvider()
