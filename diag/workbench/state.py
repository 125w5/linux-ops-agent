from __future__ import annotations

from dataclasses import dataclass, field
from threading import Condition, RLock
from typing import Any

from diag.core.models import DiagnosisPlan
from diag.dashboard.view_model import DashboardViewModel
from diag.permissions.mode import PermissionMode
from diag.workbench.message import WorkbenchMessage


@dataclass
class ApprovalState:
    command: str = ""
    reason: str = ""
    pending: bool = False
    decision: bool | None = None


@dataclass
class WorkbenchState:
    target: str = "localhost"
    mode: PermissionMode = PermissionMode.DEMO
    task_type: str = "disk"
    service: str = "nginx"
    provider: str | None = None
    model: str | None = None
    profile: str | None = None
    style: str | None = None
    skill: str | None = None
    user_input: str = ""
    status: str = "idle"
    risk: str = "unknown"
    raw_expanded: bool = False
    running: bool = False
    exit_requested: bool = False
    current_plan: DiagnosisPlan | None = None
    outcome_report_path: str = ""
    outcome_json_path: str = ""
    messages: list[WorkbenchMessage] = field(default_factory=list)
    dashboard: DashboardViewModel = field(default_factory=DashboardViewModel)
    approval: ApprovalState = field(default_factory=ApprovalState)
    lock: RLock = field(default_factory=RLock)
    approval_condition: Condition = field(init=False)

    def __post_init__(self) -> None:
        self.approval_condition = Condition(self.lock)
        self.dashboard.target = self.target
        self.dashboard.task = self.task_type
        self.dashboard.mode = self.mode.value

    def add_message(self, role: str, content: str, **metadata: Any) -> None:
        with self.lock:
            self.messages.append(WorkbenchMessage(role, content, metadata))
            self.messages = self.messages[-200:]

    def apply_event(self, event_type: str, payload: dict[str, Any]) -> None:
        with self.lock:
            self.status = event_type
            self.dashboard.apply(event_type, payload)
            if event_type == "PlanCreated":
                self.add_message("agent", f"Plan ready: {len(payload.get('steps', []))} step(s)")
            elif event_type == "ToolStarted":
                self.add_message("tool", f"running: {payload.get('command', '')}")
            elif event_type == "ToolFinished":
                self.add_message("tool", f"finished: {payload.get('command', '')} -> {payload.get('status')}")
            elif event_type == "EvidenceAdded":
                self.add_message("agent", f"Evidence updated: {len(payload.get('items', []))} item(s)")
            elif event_type == "ReportWritten":
                self.outcome_report_path = str(payload.get("markdown_path", ""))
                self.outcome_json_path = str(payload.get("json_path", ""))
            elif event_type == "SessionEnded":
                self.risk = str(payload.get("risk_level", self.risk))

    def set_resources(self, snapshot: dict[str, Any]) -> None:
        with self.lock:
            self.dashboard.apply_resources(snapshot)
