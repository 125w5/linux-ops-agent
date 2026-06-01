from __future__ import annotations

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalCapabilities:
    is_tty: bool
    width: int
    color: bool
    ci: bool
    recommended_view: str


def detect_capabilities(width: int | None = None, is_tty: bool | None = None) -> TerminalCapabilities:
    terminal_width = width if width is not None else 100
    if width is None:
        try:
            import shutil

            terminal_width = shutil.get_terminal_size((100, 24)).columns
        except OSError:
            terminal_width = 100
    tty = sys.stdout.isatty() if is_tty is None else is_tty
    ci = os.environ.get("CI", "").lower() == "true"
    color = os.environ.get("NO_COLOR") != "1" and tty
    if ci:
        view = "quiet"
    elif not tty:
        view = "normal"
    elif terminal_width < 80:
        view = "compact"
    elif terminal_width <= 120:
        view = "normal"
    else:
        view = "verbose"
    return TerminalCapabilities(tty, terminal_width, color, ci, view)
