import httpx

from backend.utils.logger import logger
from backend.utils.settings import settings


class LlamaClient:
    def __init__(self):
        config = settings.llama_cpp
        self.base_url = f"http://{config.get('host', '127.0.0.1')}:{config.get('port', 8081)}"
        self.context_length = config.get("context_length", 8192)

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
            return data.get("content", "").strip()

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


llama_client = LlamaClient()
