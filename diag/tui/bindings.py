from __future__ import annotations

from dataclasses import dataclass

from diag.utils.config_loader import load_config


CORE_BINDINGS = {
    "F1": "help",
    "F2": "raw",
    "F3": "resources",
    "F4": "report",
    "F5": "run",
    "F6": "evidence",
    "F7": "plugins",
    "F8": "model",
    "Tab": "next_pane",
    "Shift+Tab": "previous_pane",
    "Ctrl+R": "run",
    "Ctrl+A": "approve",
    "Ctrl+D": "deny",
    "Ctrl+L": "layout",
    "Ctrl+S": "save_report",
    "Esc": "close_modal",
}


@dataclass(frozen=True)
class BindingSet:
    bindings: dict[str, str]
    conflicts: dict[str, str]


def load_keybindings(plugin_bindings: dict[str, str] | None = None) -> BindingSet:
    configured = load_config().get("keybindings", {})
    merged = dict(CORE_BINDINGS)
    if isinstance(configured, dict):
        merged.update({str(key): str(value) for key, value in configured.items() if str(key) not in CORE_BINDINGS})
    conflicts: dict[str, str] = {}
    for key, action in (plugin_bindings or {}).items():
        if key in CORE_BINDINGS:
            conflicts[key] = action
            continue
        merged[key] = action
    return BindingSet(merged, conflicts)
