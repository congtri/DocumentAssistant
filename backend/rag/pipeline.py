from backend.chunking import chunk_document
from backend.chunking.heading_splitter import Chunk
from backend.document import load_document, load_all_documents
from backend.embedding.embedding_service import embedding_service
from backend.llm.llama_client import llama_client
from backend.llm.prompt_builder import prompt_builder
from backend.rag.citation import extract_citations, format_citations
from backend.retrieval.hybrid_search import hybrid_search
from backend.retrieval.reranker import reranker
from backend.retrieval.faiss_store import faiss_store
from backend.utils.logger import logger
from backend.utils.settings import settings


class RAGPipeline:
    def __init__(self):
        self.is_indexed = False

    async def ingest_documents(self, directory: str | None = None) -> int:
        doc_dir = directory or str(settings.get_path(settings.documents.get("source_dir", "documents/source")))
        documents = load_all_documents(doc_dir)

        if not documents:
            logger.warning("No documents found to ingest")
            return 0

        all_chunks = []
        for doc in documents:
            chunks = chunk_document(doc)
            all_chunks.extend(chunks)

        if all_chunks:
            hybrid_search.build_indexes(all_chunks)
            faiss_store.save()
            self.is_indexed = True
            logger.info(f"Ingested {len(documents)} documents, {len(all_chunks)} chunks")

        return len(all_chunks)

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
        config = settings.retrieval
        top_k = config.get("top_k", 5)
        results = hybrid_search.search(question, top_k=top_k)

        # Rerank if enabled
        if config.get("rerank", True) and results:
            rerank_k = config.get("rerank_top_k", 3)
            results = reranker.rerank(question, results, top_k=rerank_k)

        if not results:
            return {
                "answer": "I couldn't find relevant information in the documents.",
                "sources": [],
            }

        # Build prompt with context
        context_chunks = [
            {"text": chunk.text, "source": chunk.source, "page": chunk.page}
            for chunk, _ in results
        ]
        prompt = prompt_builder.build_rag_prompt(question, context_chunks)

        # Generate answer
        rag_config = settings.rag
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
        rag_config = settings.rag
        return await llama_client.generate(
            prompt,
            temperature=rag_config.get("temperature", 0.7),
            max_tokens=rag_config.get("max_tokens", 1024),
        )


rag_pipeline = RAGPipeline()
