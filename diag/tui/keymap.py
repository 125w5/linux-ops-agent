from __future__ import annotations

from diag.tui.actions import TuiAction
from diag.tui.bindings import load_keybindings


def action_for_key(key: str) -> TuiAction | None:
    bindings = load_keybindings().bindings
    value = bindings.get(key)
    if not value:
        return None
    try:
        return TuiAction(value)
    except ValueError:
        return None


def textual_bindings() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for key, action in load_keybindings().bindings.items():
        rows.append((key, action, action.replace("_", " ").title()))
    return rows
