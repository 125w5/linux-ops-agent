from __future__ import annotations

import time
from dataclasses import dataclass

from diag.permissions.mode import parse_permission_mode
from diag.planner.intent import infer_task
from diag.runtime.agent_loop import AgentLoop
from diag.tui.controller import TuiController
from diag.tui.fallback import render_plain_fallback, rich_available, run_rich_live_snapshot, should_use_plain_fallback, textual_available
from diag.tui.keymap import textual_bindings
from diag.tui.layouts import load_layout
from diag.tui.panes import render_pane
from diag.tui.runtime_bridge import RuntimeEventBridge
from diag.tui.state import TuiState
from diag.ui.capabilities import detect_capabilities
from diag.utils.config_loader import load_config


@dataclass(frozen=True)
class TuiOptions:
    target: str = "localhost"
    mode: str | None = "demo"
    layout: str = "default"
    task: str = "disk"
    service: str = "nginx"


def choose_layout(requested: str | None) -> str:
    caps = detect_capabilities()
    if requested:
        return requested
    if caps.width < 80:
        return "compact"
    if caps.width > 120:
        return "wide"
    return str(load_config().get("tui", {}).get("default_layout", "default"))


def render_workbench_snapshot(state: TuiState) -> str:
    layout = load_layout(state.layout)
    lines = [
        f"OpsPilot TUI Workbench [{layout.name}]",
        f"target={state.target} mode={state.mode} status={state.status} session={state.session_id or '-'}",
        "panes: " + ", ".join(layout.panes),
        f"plan_steps={len(state.plan)} evidence={len(state.evidence)} raw_lines={len(state.raw)}",
    ]
    if state.resources:
        lines.append("resources: " + ", ".join(f"{key}={value}" for key, value in state.resources.items()))
    if state.report_path:
        lines.append(f"report={state.report_path}")
    for pane in layout.panes:
        lines.extend(["", f"--- {pane} ---", render_pane(pane, state)])
    return "\n".join(lines)


def build_textual_app_class():
    try:
        from textual.app import App, ComposeResult
        from textual.widgets import Footer, Header, Static
    except Exception:
        return None

    class OpsPilotTextualApp(App):
        CSS_PATH = None
        BINDINGS = textual_bindings()

        def __init__(self, controller: TuiController, options: TuiOptions) -> None:
            super().__init__()
            self.controller = controller
            self.options = options
            self.snapshot = Static(render_workbench_snapshot(controller.state), id="snapshot")

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield self.snapshot
            yield Footer()

        def refresh_snapshot(self) -> None:
            self.snapshot.update(render_workbench_snapshot(self.controller.state))

        def action_run(self) -> None:
            self.controller.run(self.options.task, service=self.options.service)
            self.refresh_snapshot()

        def action_raw(self) -> None:
            self.controller.toggle_raw()
            self.refresh_snapshot()

        def action_resources(self) -> None:
            self.refresh_snapshot()

        def action_report(self) -> None:
            self.refresh_snapshot()

        def action_evidence(self) -> None:
            self.refresh_snapshot()

        def action_plugins(self) -> None:
            self.refresh_snapshot()

        def action_model(self) -> None:
            self.refresh_snapshot()

        def action_next_pane(self) -> None:
            self.refresh_snapshot()

        def action_previous_pane(self) -> None:
            self.refresh_snapshot()

        def action_approve(self) -> None:
            self.controller.approve()
            self.refresh_snapshot()

        def action_deny(self) -> None:
            self.controller.deny()
            self.refresh_snapshot()

        def action_layout(self) -> None:
            order = ["compact", "default", "wide", "debug"]
            current = order.index(self.controller.state.layout) if self.controller.state.layout in order else 0
            self.controller.state.layout = order[(current + 1) % len(order)]
            self.refresh_snapshot()

        def action_save_report(self) -> None:
            self.refresh_snapshot()

        def action_close_modal(self) -> None:
            self.refresh_snapshot()

        def action_help(self) -> None:
            self.refresh_snapshot()

    return OpsPilotTextualApp


def run_tui(options: TuiOptions) -> int:
    layout = choose_layout(options.layout)
    state = TuiState(target=options.target, mode=options.mode or "readonly", layout=layout)
    if should_use_plain_fallback():
        print(render_plain_fallback(state))
        return 0

    bridge = RuntimeEventBridge(state)
    controller = TuiController(state, bridge)
    if textual_available():
        app_class = build_textual_app_class()
        if app_class is not None:
            app_class(controller, options).run()
            return 0
    elif rich_available():
        print("Textual unavailable; using Rich Live fallback snapshot.")
    else:
        print("Textual/Rich unavailable; using plain fallback snapshot.")

    started = time.perf_counter()
    mode = parse_permission_mode(options.mode, demo=options.mode == "demo")
    AgentLoop().run(
        user_input=options.task,
        target=options.target,
        task_type=infer_task(options.task, options.task),
        permission_mode=mode,
        service=options.service,
        event_callback=bridge.callback(),
    )
    render_ms = int((time.perf_counter() - started) * 1000)
    state.resources["tui_render_ms"] = render_ms
    if rich_available():
        refresh = int(load_config().get("tui", {}).get("refresh_per_second", 2))
        run_rich_live_snapshot(lambda: render_workbench_snapshot(state), refresh_per_second=refresh)
    else:
        print(render_workbench_snapshot(state))
    return 0
