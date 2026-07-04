from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMClient(ABC):
    """Interface for LLM inference."""

    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate a completion from the prompt."""
        ...

    @abstractmethod
    async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> AsyncIterator[str]:
        """Stream a completion from the prompt."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM backend is available."""
        ...
