from abc import ABC, abstractmethod


class PromptBuilder(ABC):
    """Interface for building LLM prompts."""

    @abstractmethod
    def build_rag_prompt(self, question: str, context_chunks: list[dict]) -> str:
        """Build a RAG prompt with document context."""
        ...

    @abstractmethod
    def build_chat_prompt(self, question: str, history: list[dict] | None = None) -> str:
        """Build a conversational prompt."""
        ...
