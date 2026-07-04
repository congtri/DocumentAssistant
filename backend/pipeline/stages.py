"""Concrete pipeline stages for document ingestion."""

from pathlib import Path

from backend.core.logger import logger
from backend.core.config import config
from backend.document import load_all_documents
from backend.chunking import chunk_document
from backend.domain.models import Chunk
from backend.pipeline.context import PipelineContext
from backend.pipeline.stage import Stage
from backend.retrieval.hybrid_search import hybrid_search
from backend.retrieval.faiss_store import faiss_store


class LoadDocumentsStage(Stage):
    """Load documents from a directory."""

    def __init__(self, directory: str | None = None):
        self._directory = directory

    @property
    def name(self) -> str:
        return "LoadDocuments"

    def execute(self, context: PipelineContext) -> PipelineContext:
        doc_dir = self._directory or str(
            config.get_path(config.documents.get("source_dir", "documents/source"))
        )
        documents = load_all_documents(doc_dir)

        if not documents:
            context.add_error("No documents found to ingest")
            return context

        context.documents = documents
        context.metadata["source_dir"] = doc_dir
        logger.info(f"Loaded {len(documents)} documents")
        return context


class ChunkDocumentsStage(Stage):
    """Split documents into chunks."""

    @property
    def name(self) -> str:
        return "ChunkDocuments"

    def execute(self, context: PipelineContext) -> PipelineContext:
        all_chunks: list[Chunk] = []
        for doc in context.documents:
            try:
                chunks = chunk_document(doc)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to chunk {doc.name}: {e}")
                context.add_error(f"Chunking failed for {doc.name}: {e}")

        context.chunks = all_chunks
        logger.info(f"Created {len(all_chunks)} chunks")
        return context


class BuildIndexesStage(Stage):
    """Build search indexes from chunks."""

    @property
    def name(self) -> str:
        return "BuildIndexes"

    def execute(self, context: PipelineContext) -> PipelineContext:
        if not context.chunks:
            context.add_error("No chunks to index")
            return context

        hybrid_search.build_index(context.chunks)
        faiss_store.save()
        context.metadata["chunks_indexed"] = len(context.chunks)
        logger.info(f"Indexed {len(context.chunks)} chunks")
        return context
