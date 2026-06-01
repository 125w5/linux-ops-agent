from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from diag.tui.events import TuiEvent


@dataclass
class TuiState:
    target: str = "localhost"
    mode: str = "demo"
    layout: str = "default"
    status: str = "idle"
    session_id: str = ""
    plan: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    raw: list[str] = field(default_factory=list)
    transcript: list[str] = field(default_factory=list)
    audit: list[str] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)
    report_path: str = ""
    events: list[TuiEvent] = field(default_factory=list)

    def apply(self, event: TuiEvent) -> None:
        self.events.append(event)
        self.transcript.append(f"{event.type}: {event.payload}")
        if event.type in {"ToolStarted", "ToolFinished", "ApprovalRequired", "ApprovalResolved", "ReportWritten", "ResourceUpdated"}:
            self.audit.append(f"{event.type}: {event.payload}")
        self.status = event.type
        if event.type == "SessionStarted":
            self.session_id = str(event.payload.get("session_id", ""))
        elif event.type == "PlanCreated":
            self.plan = list(event.payload.get("steps", []))
        elif event.type == "ToolFinished":
            command = event.payload.get("command", "")
            status = event.payload.get("status", "")
            truncated = " truncated" if event.payload.get("truncated") else ""
            self.raw.append(f"{command} -> {status}{truncated}".strip())
            self.raw = self.raw[-200:]
        elif event.type == "EvidenceAdded":
            self.evidence = list(event.payload.get("items", []))
        elif event.type == "ReportWritten":
            self.report_path = str(event.payload.get("markdown_path", ""))
        elif event.type == "ResourceUpdated":
            self.resources = dict(event.payload)
