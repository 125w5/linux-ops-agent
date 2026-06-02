from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Iterable

from diag.ai.errors import LLMConfigurationError, LLMRequestError
from diag.ai.message import LLMMessage, LLMResponse, ProviderHealth
from diag.ai.provider import LLMProvider
from diag.ai.remote_url_validator import validate_remote_api_url
from diag.utils.env_vars import get_env_var


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(
        self,
        model: str = "claude-3-5-haiku-latest",
        api_key_env: str = "ANTHROPIC_API_KEY",
        base_url: str = "https://api.anthropic.com",
        timeout: int = 30,
        max_tokens: int = 1024,
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.base_url = validate_remote_api_url(base_url).rstrip("/")
        self.timeout = timeout
        self.max_tokens = max_tokens

    def _api_key(self) -> str | None:
        return get_env_var(self.api_key_env)

    def healthcheck(self) -> ProviderHealth:
        if not self._api_key():
            return ProviderHealth(False, self.name, f"Missing API key env var: {self.api_key_env}")
        return ProviderHealth(True, self.name, "configuration looks usable")

    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        health = self.healthcheck()
        if not health.ok:
            raise LLMConfigurationError(health.message)
        system_parts = [message.content for message in messages if message.role == "system"]
        user_messages = [message for message in messages if message.role != "system"]
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": "\n".join(system_parts) if system_parts else None,
            "messages": [{"role": message.role, "content": message.content} for message in user_messages],
        }
        data = json.dumps({key: value for key, value in payload.items() if value is not None}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key() or "",
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LLMRequestError(f"{self.name} request failed: {exc}") from exc
        parts = body.get("content", [])
        content = "".join(part.get("text", "") for part in parts if part.get("type") == "text")
        return LLMResponse(content=content, model=self.model, provider=self.name)

    def stream(self, messages: list[LLMMessage]) -> Iterable[str]:
        yield self.complete(messages).content
