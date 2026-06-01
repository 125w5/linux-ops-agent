from __future__ import annotations

from diag.ai.providers.openai_compatible_provider import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, model: str = "gpt-4o-mini", api_key_env: str = "OPENAI_API_KEY", base_url: str = "https://api.openai.com/v1", timeout: int = 30, max_tokens: int = 1024) -> None:
        super().__init__(base_url=base_url, api_key_env=api_key_env, model=model, provider_name="openai", timeout=timeout, max_tokens=max_tokens)
