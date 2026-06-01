from __future__ import annotations

from diag.tui.pagination import page_lines
from diag.tui.state import TuiState


def render(state: TuiState, active: bool = False, page: int = 0) -> str:
    prefix = "> " if active else ""
    body = page_lines(state.audit, page=page, page_size=50)
    return prefix + "AuditPane\n" + (body.text or "(empty)") + ("\n[truncated]" if body.truncated else "")
