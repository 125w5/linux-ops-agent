from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from diag.core.models import CommandResult, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.runtime.event import RuntimeEvent


class Transcript:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.events: list[RuntimeEvent] = []

    def append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append(RuntimeEvent(event_type, payload))

    def append_user_input(self, user_input: str) -> None:
        self.append_event("user_input", {"user_input": user_input})

    def append_plan(self, plan: DiagnosisPlan) -> None:
        self.append_event(
            "plan",
            {
                "task_type": plan.task_type,
                "target": plan.target,
                "steps": [
                    {
                        "id": step.id,
                        "name": step.name,
                        "tool_name": step.tool_name,
                        "tool_args": step.tool_args,
                        "command": step.command,
                        "risk": step.risk.value,
                    }
                    for step in plan.steps
                ],
            },
        )

    def append_command_result(self, step: DiagnosisStep, result: CommandResult) -> None:
        self.append_event(
            "command_result",
            {
                "step_id": step.id,
                "tool_name": step.tool_name,
                "command": result.command,
                "result": result.to_dict(),
            },
        )

    def append_evidence(self, evidence: list[EvidenceItem]) -> None:
        self.append_event("evidence", {"items": [item.to_dict() for item in evidence]})

    def append_report_path(self, markdown_path: str | None, json_path: str | None) -> None:
        self.append_event("report_path", {"markdown_path": markdown_path, "json_path": json_path})

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "events": [
                {"type": event.type, "timestamp": event.timestamp, "payload": event.payload}
                for event in self.events
            ],
        }

    def write(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.session_id}.transcript.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path
