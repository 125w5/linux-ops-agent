from __future__ import annotations

from diag.tui.panes import render_raw_pane
from diag.tui.state import TuiState


def render(state: TuiState, active: bool = False, expanded: bool = False) -> str:
    return ("> " if active else "") + render_raw_pane(state, expanded=expanded)
