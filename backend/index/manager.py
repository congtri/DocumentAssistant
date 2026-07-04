"""Index lifecycle management."""

from backend.core.interfaces.index_manager import IndexManager
from backend.core.config import config
from backend.core.logger import logger
from backend.domain.models import Chunk
from backend.retrieval.faiss_store import faiss_store
from backend.retrieval.bm25_store import bm25_store


class IndexService(IndexManager):
    """Manages building, loading, and deleting search indexes."""

    def build(self, chunks: list[Chunk]) -> None:
        if not chunks:
            logger.warning("No chunks to build indexes from")
            return
        faiss_store.build_index(chunks)
        bm25_store.build_index(chunks)
        faiss_store.save()
        logger.info(f"Built indexes with {len(chunks)} chunks")

    def delete(self) -> None:
        index_dir = config.get_path(config.data.get("indexes_dir", "data/indexes"))
        if index_dir.exists():
            for f in index_dir.iterdir():
                f.unlink()
            logger.info("Deleted all indexes")

    def exists(self) -> bool:
        index_dir = config.get_path(config.data.get("indexes_dir", "data/indexes"))
        faiss_path = index_dir / "faiss.index"
        return faiss_path.exists()

    def load(self) -> bool:
        loaded = faiss_store.load()
        if loaded and faiss_store.chunks:
            bm25_store.build_index(faiss_store.chunks)
        return loaded

    def rebuild(self, chunks: list[Chunk]) -> None:
        """Delete existing indexes and rebuild from chunks."""
        self.delete()
        self.build(chunks)


index_service = IndexService()
