"""Abstract interfaces for all replaceable components."""

from backend.core.interfaces.document_loader import DocumentLoader
from backend.core.interfaces.chunk_strategy import ChunkStrategy
from backend.core.interfaces.embedding_provider import EmbeddingProvider
from backend.core.interfaces.retriever import Retriever
from backend.core.interfaces.reranker import Reranker
from backend.core.interfaces.prompt_builder import PromptBuilder
from backend.core.interfaces.llm_client import LLMClient
from backend.core.interfaces.storage_provider import StorageProvider
from backend.core.interfaces.index_manager import IndexManager

__all__ = [
    "DocumentLoader",
    "ChunkStrategy",
    "EmbeddingProvider",
    "Retriever",
    "Reranker",
    "PromptBuilder",
    "LLMClient",
    "StorageProvider",
    "IndexManager",
]
