import re
from collections.abc import AsyncIterator

import httpx

from backend.core.interfaces.llm_client import LLMClient
from backend.core.logger import logger
from backend.core.config import config


class LlamaClient(LLMClient):
    def __init__(self):
        llama_config = config.llama_cpp
        self.base_url = f"http://{llama_config.get('host', '127.0.0.1')}:{llama_config.get('port', 8081)}"
        self.context_length = llama_config.get("context_length", 8192)

    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": max_tokens,
            "stop": ["<|im_end|>", "<|endoftext|>"],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/completion", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("content", "").strip()
            return self._clean_thinking_tokens(content)

    async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024):
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": max_tokens,
            "stop": ["<|im_end|>", "<|endoftext|>"],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/completion", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        chunk = json.loads(line[6:])
                        content = chunk.get("content", "")
                        if content:
                            yield content

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"llama.cpp health check failed: {e}")
            return False

    def _clean_thinking_tokens(self, text: str) -> str:
        """Strip Qwen thinking/reasoning markers, keep only final answer."""
        match = re.search(
            r"\[Start of final answer\]\s*(.*?)\s*\[End of final answer\]",
            text, re.DOTALL
        )
        if match:
            return match.group(1).strip()
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return text


llama_client = LlamaClient()
