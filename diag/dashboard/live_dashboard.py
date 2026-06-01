from __future__ import annotations

from collections.abc import Callable
from typing import Any

from diag.core.models import DiagnosisOutcome
from diag.dashboard.renderers import command_discovery_text, render_plain_dashboard, render_rich_dashboard
from diag.dashboard.system_monitor import SystemMonitor
from diag.dashboard.view_model import DashboardViewModel
from diag.runtime.event import RuntimeEvent


Runner = Callable[[Callable[[str, dict[str, Any]], None]], DiagnosisOutcome]


def rich_available() -> bool:
    try:
        import rich  # noqa: F401
    except Exception:
        return False
    return True


class LiveDashboard:
    def __init__(self, view_model: DashboardViewModel | None = None, *, live: bool = True, raw_expanded: bool = False) -> None:
        self.vm = view_model or DashboardViewModel()
        self.live = live
        self.raw_expanded = raw_expanded
        self.monitor = SystemMonitor(on_sample=self._apply_resource_sample)
        self._live_handle: Any = None

    def run(self, runner: Runner) -> DiagnosisOutcome:
        self.monitor.sample_once()
        if self.live and rich_available():
            from rich.live import Live

            with Live(render_rich_dashboard(self.vm, raw_expanded=self.raw_expanded), refresh_per_second=4, transient=False) as live:
                self._live_handle = live
                self.monitor.start()
                try:
                    outcome = runner(self.event_callback)
                    self.vm.complete_from_outcome(outcome)
                    self.refresh()
                    return outcome
                finally:
                    self.monitor.stop()
                    self._live_handle = None

        self.monitor.start()
        try:
            outcome = runner(self.event_callback)
            self.vm.complete_from_outcome(outcome)
            print(render_plain_dashboard(self.vm, raw_expanded=self.raw_expanded))
            return outcome
        finally:
            self.monitor.stop()

    def event_callback(self, event_type: str, payload: dict[str, Any]) -> None:
        self.vm.apply(RuntimeEvent(event_type, payload))
        self.refresh()

    def refresh(self) -> None:
        if self._live_handle is not None:
            self._live_handle.update(render_rich_dashboard(self.vm, raw_expanded=self.raw_expanded))

    def _apply_resource_sample(self, snapshot: dict[str, Any]) -> None:
        self.vm.apply_resources(snapshot)
        self.refresh()


def render_command_discovery() -> str:
    return command_discovery_text()
