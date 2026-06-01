from __future__ import annotations

from diag.ai.providers.openai_compatible_provider import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434/v1", timeout: int = 30, max_tokens: int = 1024) -> None:
        normalized = base_url.rstrip("/")
        if not normalized.endswith("/v1"):
            normalized = f"{normalized}/v1"
        super().__init__(base_url=normalized, api_key_env=None, model=model, provider_name="ollama", timeout=timeout, max_tokens=max_tokens)
