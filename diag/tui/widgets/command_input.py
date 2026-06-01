from __future__ import annotations

from diag.tui.panes import render_command_input
from diag.tui.state import TuiState


def render(state: TuiState, active: bool = False) -> str:
    prefix = "> " if active else ""
    return prefix + render_command_input(state)
