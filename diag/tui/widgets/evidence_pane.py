from __future__ import annotations

from diag.tui.panes import render_evidence_pane
from diag.tui.state import TuiState


def render(state: TuiState, active: bool = False) -> str:
    return ("> " if active else "") + render_evidence_pane(state)
