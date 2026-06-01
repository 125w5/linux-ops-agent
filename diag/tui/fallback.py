from __future__ import annotations

import os
import time

from diag.tui.state import TuiState
from diag.ui.capabilities import detect_capabilities


def should_use_plain_fallback() -> bool:
    caps = detect_capabilities()
    return caps.ci or not caps.is_tty


def render_plain_fallback(state: TuiState) -> str:
    lines = [
        "OpsPilot TUI fallback",
        f"layout={state.layout} target={state.target} mode={state.mode} status={state.status}",
        "TUI is unavailable in CI/non-TTY; use `diag chat` or `diag diagnose` for full output.",
    ]
    if state.report_path:
        lines.append(f"report={state.report_path}")
    return "\n".join(lines)


def textual_available() -> bool:
    try:
        import textual  # noqa: F401
    except Exception:
        return False
    return True


def rich_available() -> bool:
    try:
        import rich  # noqa: F401
    except Exception:
        return False
    return True


def run_rich_live_snapshot(render, refresh_per_second: int = 2, iterations: int = 1) -> None:
    delay = 1 / max(1, refresh_per_second)
    if rich_available():
        from rich.live import Live
        from rich.panel import Panel

        with Live(Panel(render()), refresh_per_second=refresh_per_second, transient=False) as live:
            for _ in range(max(1, iterations) - 1):
                time.sleep(delay)
                live.update(Panel(render()))
        return
    for _ in range(max(1, iterations)):
        print(render())
        time.sleep(delay)
