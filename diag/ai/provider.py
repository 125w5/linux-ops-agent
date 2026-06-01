from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from diag.ai.message import LLMMessage, LLMResponse, ProviderHealth


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    def stream(self, messages: list[LLMMessage]) -> Iterable[str]:
        raise NotImplementedError

    @abstractmethod
    def healthcheck(self) -> ProviderHealth:
        raise NotImplementedError
