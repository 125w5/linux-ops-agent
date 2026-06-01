from __future__ import annotations

from diag.ui.capabilities import detect_capabilities


def choose_view(requested: str | None) -> str:
    if requested:
        return requested
    return detect_capabilities().recommended_view
