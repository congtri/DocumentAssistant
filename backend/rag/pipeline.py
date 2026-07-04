from backend.chunking import chunk_document
from backend.document import load_document, load_all_documents
from backend.domain.models import Chunk
from backend.embedding.embedding_service import embedding_service
from backend.llm.llama_client import llama_client
from backend.llm.prompt_builder import prompt_builder
from backend.pipeline.engine import PipelineEngine
from backend.pipeline.stages import LoadDocumentsStage, ChunkDocumentsStage, BuildIndexesStage
from backend.rag.citation import extract_citations, format_citations
from backend.retrieval.hybrid_search import hybrid_search
from backend.retrieval.reranker import reranker
from backend.retrieval.bm25_store import bm25_store
from backend.retrieval.faiss_store import faiss_store
from backend.core.logger import logger
from backend.core.config import config


class RAGPipeline:
    def __init__(self):
        self.is_indexed = faiss_store.load()
        if self.is_indexed and faiss_store.chunks:
            bm25_store.build_index(faiss_store.chunks)

    async def ingest_documents(self, directory: str | None = None) -> int:
        pipeline = PipelineEngine([
            LoadDocumentsStage(directory),
            ChunkDocumentsStage(),
            BuildIndexesStage(),
        ])
        result = pipeline.execute()

        if result.has_errors and not result.chunks:
            logger.warning(f"Ingestion errors: {result.errors}")
            return 0

        self.is_indexed = True
        return result.metadata.get("chunks_indexed", 0)

    async def query(self, question: str) -> dict:
        if not self.is_indexed:
            # Try loading saved index
            if not faiss_store.load():
                return {
                    "answer": "No documents have been indexed yet. Please ingest documents first.",
                    "sources": [],
                }
            self.is_indexed = True

        # Retrieve relevant chunks
        retrieval_config = config.retrieval
        top_k = retrieval_config.get("top_k", 5)
        results = hybrid_search.search(question, top_k=top_k)

        # Rerank if enabled
        if retrieval_config.get("rerank", True) and results:
            rerank_k = retrieval_config.get("rerank_top_k", 3)
            results = reranker.rerank(question, results, top_k=rerank_k)

        if not results:
            return {
                "answer": "I couldn't find relevant information in the documents.",
                "sources": [],
            }

        # Build prompt with context, packing as much as fits
        max_context = config.rag.get("max_context_length", 6144)
        context_chunks = []
        total_len = 0
        for chunk, _ in results:
            chunk_text = chunk.text
            if total_len + len(chunk_text) > max_context:
                # Include partial if significant portion fits
                remaining = max_context - total_len
                if remaining > 200:
                    context_chunks.append({"text": chunk_text[:remaining], "source": chunk.source, "page": chunk.page})
                break
            context_chunks.append({"text": chunk_text, "source": chunk.source, "page": chunk.page})
            total_len += len(chunk_text)

        prompt = prompt_builder.build_rag_prompt(question, context_chunks)

        # Generate answer
        rag_config = config.rag
        answer = await llama_client.generate(
            prompt,
            temperature=rag_config.get("temperature", 0.7),
            max_tokens=rag_config.get("max_tokens", 1024),
        )

        # Extract citations
        citations = extract_citations(results)
        citation_text = format_citations(citations)

        return {
            "answer": answer + citation_text,
            "sources": [
                {"source": c.source, "page": c.page, "score": s}
                for c, s in results
            ],
        }

    async def chat(self, question: str, history: list[dict] | None = None) -> str:
        prompt = prompt_builder.build_chat_prompt(question, history)
        rag_config = config.rag
        return await llama_client.generate(
            prompt,
            temperature=rag_config.get("temperature", 0.7),
            max_tokens=rag_config.get("max_tokens", 1024),
        )


rag_pipeline = RAGPipeline()
