from __future__ import annotations

from collections.abc import Callable
from typing import Any


Emit = Callable[[str, dict[str, Any]], None]


def emit_assistant_stream(emit: Emit, session_id: str, content: str) -> None:
    emit("AssistantMessageStarted", {"session_id": session_id})
    if content:
        for chunk in _chunks(content):
            emit("AssistantDelta", {"session_id": session_id, "delta": chunk})
    emit("AssistantMessageDone", {"session_id": session_id})


def _chunks(text: str, size: int = 24) -> list[str]:
    return [text[index : index + size] for index in range(0, len(text), size)]
