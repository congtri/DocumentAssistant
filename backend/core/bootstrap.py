"""Bootstrap module: wires all concrete implementations to interfaces.

Import this module at application startup to register all dependencies.
"""

from backend.core.dependency import container
from backend.core.interfaces import (
    ChunkStrategy,
    DocumentLoader,
    EmbeddingProvider,
    IndexManager,
    LLMClient,
    PromptBuilder,
    Reranker,
    Retriever,
    StorageProvider,
)
from backend.chunking.heading_splitter import heading_splitter
from backend.embedding.embedding_service import embedding_service
from backend.index.manager import index_service
from backend.llm.llama_client import llama_client
from backend.llm.prompt_builder import prompt_builder
from backend.retrieval.hybrid_search import hybrid_search
from backend.retrieval.reranker import reranker
from backend.storage.filesystem import FilesystemStorage


def bootstrap() -> None:
    """Register all default implementations in the DI container."""
    container.register(EmbeddingProvider, embedding_service)
    container.register(Retriever, hybrid_search)
    container.register(Reranker, reranker)
    container.register(LLMClient, llama_client)
    container.register(PromptBuilder, prompt_builder)
    container.register(IndexManager, index_service)
    container.register(ChunkStrategy, heading_splitter)
    container.register(StorageProvider, FilesystemStorage())
