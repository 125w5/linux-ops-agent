from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LLMMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str


@dataclass(frozen=True)
class ProviderHealth:
    ok: bool
    provider: str
    message: str
