from __future__ import annotations

import time

from diag.workbench.panes.conversation_pane import render_conversation_pane
from diag.workbench.panes.evidence_pane import render_evidence_pane
from diag.workbench.panes.monitor_pane import render_monitor_pane
from diag.workbench.panes.plan_pane import render_plan_pane
from diag.workbench.panes.raw_pane import render_raw_pane
from diag.workbench.panes.report_pane import render_report_pane
from diag.workbench.panes.resources_pane import render_resources_pane
from diag.workbench.panes.statusline import render_statusline
from diag.workbench.slash_commands import help_text
from diag.workbench.state import WorkbenchState


class WorkbenchRenderer:
    def __init__(self, state: WorkbenchState) -> None:
        self.state = state

    def snapshot(self) -> str:
        started = time.perf_counter()
        with self.state.lock:
            sections = [
                render_statusline(self.state),
                "",
                render_conversation_pane(self.state),
                "",
                render_monitor_pane(self.state),
                "",
                render_plan_pane(self.state),
                "",
                render_evidence_pane(self.state),
                "",
                render_raw_pane(self.state),
                "",
                render_report_pane(self.state),
                "",
                render_resources_pane(self.state),
            ]
            if self.state.approval.pending:
                sections.extend(["", f"Approval required: {self.state.approval.command}", self.state.approval.reason, "输入 /approve 或 /deny"])
            sections.extend(["", "Commands", help_text("/")])
            render_ms = int((time.perf_counter() - started) * 1000)
            self.state.dashboard.resources["render_ms"] = render_ms
            return "\n".join(sections)

    def render(self, output_func=print) -> None:
        output_func(self.snapshot())
