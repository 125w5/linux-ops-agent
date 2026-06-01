from __future__ import annotations

from collections.abc import Callable
from typing import Any

from diag.engine.protocol import dumps, event


class EventStream:
    def __init__(self, write_line: Callable[[str], None]) -> None:
        self.write_line = write_line

    def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.write_line(dumps(event(event_type, payload or {})))

    def callback(self) -> Callable[[str, dict[str, Any]], None]:
        return self.emit
