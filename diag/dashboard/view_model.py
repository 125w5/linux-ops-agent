from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from diag.core.models import DiagnosisOutcome
from diag.runtime.event import RuntimeEvent


@dataclass
class ToolCallView:
    step_id: str
    name: str = ""
    command: str = ""
    tool_name: str = ""
    risk: str = "safe_readonly"
    status: str = "pending"
    detail: str = ""
    stdout_bytes: int = 0
    truncated: bool = False


@dataclass
class DashboardViewModel:
    session_id: str = ""
    task: str = ""
    target: str = "localhost"
    mode: str = "readonly"
    provider: str = "mock"
    model: str = ""
    risk: str = "unknown"
    status: str = "idle"
    plan: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[ToolCallView] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)
    report_path: str = ""
    json_path: str = ""
    raw_summary: list[str] = field(default_factory=list)
    report_preview: list[str] = field(default_factory=list)
    events_seen: int = 0

    def apply(self, event: RuntimeEvent | str, payload: dict[str, Any] | None = None) -> None:
        if isinstance(event, RuntimeEvent):
            event_type = event.type
            data = event.payload
        else:
            event_type = event
            data = payload or {}

        self.events_seen += 1
        self.status = event_type

        if event_type == "SessionStarted":
            self.session_id = str(data.get("session_id", self.session_id))
            self.target = str(data.get("target", self.target))
            self.task = str(data.get("task_type", self.task))
            self.mode = str(data.get("mode", self.mode))
            self.provider = str(data.get("provider", self.provider or "mock"))
            self.model = str(data.get("model", self.model))
        elif event_type == "PlanCreated":
            self.task = str(data.get("task_type", self.task))
            self.target = str(data.get("target", self.target))
            self.plan = list(data.get("steps", []))
            self.tool_calls = [
                ToolCallView(
                    step_id=str(step.get("id", "")),
                    name=str(step.get("name", "")),
                    command=str(step.get("command", "")),
                    tool_name=str(step.get("tool_name", "") or step.get("id", "")),
                    risk=str(step.get("risk", "safe_readonly")),
                )
                for step in self.plan
            ]
        elif event_type == "ToolStarted":
            call = self._ensure_tool_call(data)
            call.status = "running"
            call.detail = "running"
        elif event_type == "ToolFinished":
            call = self._ensure_tool_call(data)
            status = data.get("status", "")
            call.status = "skipped" if status == "skipped" else "done" if status == 0 else f"rc={status}"
            call.detail = call.status
            call.truncated = bool(data.get("truncated", False))
            call.stdout_bytes = int(data.get("stdout_bytes", 0) or 0)
            raw = f"{call.command} -> {call.status}"
            if call.truncated:
                raw += " (truncated)"
            self.raw_summary.append(raw)
            self.raw_summary = self.raw_summary[-20:]
        elif event_type == "ApprovalRequired":
            call = self._ensure_tool_call(data)
            call.status = "approval"
            call.detail = str(data.get("reason", "approval required"))
            call.risk = str(data.get("risk_level", call.risk))
        elif event_type == "ApprovalResolved":
            call = self._ensure_tool_call(data)
            call.status = "approved" if data.get("approved") else "blocked"
            call.detail = str(data.get("reason", call.status))
        elif event_type == "EvidenceAdded":
            self.evidence.extend(list(data.get("items", [])))
            self.evidence = self.evidence[-20:]
        elif event_type == "ResourceUpdated":
            self.resources.update(data)
        elif event_type == "ReportWritten":
            self.report_path = str(data.get("markdown_path", self.report_path))
            self.json_path = str(data.get("json_path", self.json_path))
        elif event_type == "SessionEnded":
            self.risk = str(data.get("risk_level", self.risk))

    def apply_resources(self, snapshot: dict[str, Any]) -> None:
        self.resources.update(snapshot)

    def complete_from_outcome(self, outcome: DiagnosisOutcome) -> None:
        self.session_id = outcome.session_id
        self.target = outcome.target
        self.task = outcome.task_type
        self.risk = outcome.risk_level
        self.report_path = outcome.markdown_path or self.report_path
        self.json_path = outcome.json_path or self.json_path
        self.report_preview = [f"[{item.severity}] {item.content}" for item in outcome.evidence[:6]]
        if not self.evidence:
            self.evidence = [item.to_dict() for item in outcome.evidence]

    def _ensure_tool_call(self, data: dict[str, Any]) -> ToolCallView:
        step_id = str(data.get("step_id", ""))
        for call in self.tool_calls:
            if call.step_id == step_id:
                if data.get("command"):
                    call.command = str(data.get("command"))
                if data.get("tool_name"):
                    call.tool_name = str(data.get("tool_name"))
                return call

        call = ToolCallView(
            step_id=step_id,
            command=str(data.get("command", "")),
            tool_name=str(data.get("tool_name", "") or step_id),
        )
        self.tool_calls.append(call)
        return call
