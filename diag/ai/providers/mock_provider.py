from __future__ import annotations

import json
from collections.abc import Iterable

from diag.ai.message import LLMMessage, LLMResponse, ProviderHealth
from diag.ai.provider import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def __init__(self, model: str = "mock-diagnosis-v1") -> None:
        self.model = model

    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        prompt = "\n".join(message.content for message in messages)
        if "planner" in prompt.lower():
            content = json.dumps({"task": "disk", "tool_calls": []})
        elif "risk" in prompt.lower():
            content = "Mock risk review: safety checker remains authoritative."
        elif "report" in prompt.lower():
            content = "Mock report polish: evidence preserved."
        else:
            content = "Mock summary: rule-based diagnosis evidence reviewed."
        return LLMResponse(content=content, model=self.model, provider=self.name)

    def stream(self, messages: list[LLMMessage]) -> Iterable[str]:
        yield self.complete(messages).content

    def healthcheck(self) -> ProviderHealth:
        return ProviderHealth(True, self.name, "mock provider ready")
