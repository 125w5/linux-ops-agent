from __future__ import annotations

from diag.tui.panes import render_status_bar
from diag.tui.state import TuiState


def render(state: TuiState, active: bool = False) -> str:
    prefix = "> " if active else ""
    return prefix + render_status_bar(state)
