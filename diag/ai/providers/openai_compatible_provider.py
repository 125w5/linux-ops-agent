from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Iterable

from diag.ai.errors import LLMConfigurationError, LLMRequestError
from diag.ai.message import LLMMessage, LLMResponse, ProviderHealth
from diag.ai.provider import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    name = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        api_key_env: str | None,
        model: str,
        provider_name: str = "openai-compatible",
        timeout: int = 30,
        max_tokens: int = 1024,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.model = model
        self.name = provider_name
        self.timeout = timeout
        self.max_tokens = max_tokens

    def _api_key(self) -> str | None:
        return os.environ.get(self.api_key_env) if self.api_key_env else None

    def healthcheck(self) -> ProviderHealth:
        if self.api_key_env and not self._api_key():
            return ProviderHealth(False, self.name, f"Missing API key env var: {self.api_key_env}")
        return ProviderHealth(True, self.name, "configuration looks usable")

    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        health = self.healthcheck()
        if not health.ok:
            raise LLMConfigurationError(health.message)
        payload = {
            "model": self.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        api_key = self._api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        request = urllib.request.Request(f"{self.base_url}/chat/completions", data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LLMRequestError(f"{self.name} request failed: {exc}") from exc
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return LLMResponse(content=content, model=self.model, provider=self.name)

    def stream(self, messages: list[LLMMessage]) -> Iterable[str]:
        yield self.complete(messages).content
