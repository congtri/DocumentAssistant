from backend.utils.settings import settings


class PromptBuilder:
    def __init__(self):
        rag_config = settings.rag
        self.system_prompt = rag_config.get("system_prompt", "You are a helpful assistant.")

    def build_rag_prompt(self, question: str, context_chunks: list[dict]) -> str:
        context_text = self._format_context(context_chunks)
        return (
            f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Use the following document excerpts to answer the question. "
            f"Read all excerpts carefully before answering.\n\n"
            f"--- DOCUMENT EXCERPTS ---\n{context_text}\n--- END EXCERPTS ---\n\n"
            f"Question: {question}\n\n"
            f"Provide a detailed, accurate answer based on the excerpts above.<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

    def build_chat_prompt(self, question: str, history: list[dict] | None = None) -> str:
        prompt = f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        prompt += f"<|im_start|>user\n{question}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"
        return prompt

    def _format_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("source", "Unknown")
            page = chunk.get("page", "")
            text = chunk.get("text", "")
            header = f"[{i}] {source}"
            if page:
                header += f" (page {page})"
            parts.append(f"{header}\n{text}")
        return "\n\n---\n\n".join(parts)


prompt_builder = PromptBuilder()
