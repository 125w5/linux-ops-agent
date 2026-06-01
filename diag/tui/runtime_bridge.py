from __future__ import annotations

from collections.abc import Callable

from diag.tui.events import TuiEvent
from diag.tui.state import TuiState


class RuntimeEventBridge:
    def __init__(self, state: TuiState | None = None) -> None:
        self.state = state or TuiState()
        self.subscribers: list[Callable[[TuiEvent], None]] = [self.state.apply]

    def emit(self, event_type: str, payload: dict | None = None) -> None:
        event = TuiEvent(event_type, payload or {})
        for subscriber in list(self.subscribers):
            subscriber(event)

    def callback(self) -> Callable[[str, dict], None]:
        return self.emit
