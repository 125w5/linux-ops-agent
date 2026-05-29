from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RiskLevel(str, Enum):
    SAFE_READONLY = "safe_readonly"
    LOW_RISK = "low_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class DiagnosisStep:
    id: str
    name: str
    command: str
    risk: RiskLevel = RiskLevel.SAFE_READONLY
    required: bool = True
    tool_name: str | None = None
    tool_args: dict[str, str] = field(default_factory=dict)


@dataclass
class CommandResult:
    command: str
    target: str
    stdout: str
    stderr: str
    return_code: int
    duration_ms: int
    risk_level: str
    executed_at: str = field(default_factory=utc_now)
    skipped: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    evidence_type: str
    content: str
    severity: str = "info"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosisPlan:
    task_type: str
    target: str
    steps: list[DiagnosisStep]


@dataclass
class DiagnosisOutcome:
    session_id: str
    user_input: str
    target: str
    task_type: str
    plan: DiagnosisPlan
    results: list[CommandResult]
    evidence: list[EvidenceItem]
    root_causes: list[str]
    suggestions: list[str]
    risk_level: str
    started_at: str
    ended_at: str
    markdown_path: str | None = None
    json_path: str | None = None

    @classmethod
    def start(cls, user_input: str, plan: DiagnosisPlan) -> "DiagnosisOutcome":
        now = utc_now()
        return cls(
            session_id=str(uuid4()),
            user_input=user_input,
            target=plan.target,
            task_type=plan.task_type,
            plan=plan,
            results=[],
            evidence=[],
            root_causes=[],
            suggestions=[],
            risk_level="unknown",
            started_at=now,
            ended_at=now,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_input": self.user_input,
            "target": self.target,
            "task_type": self.task_type,
            "plan": {
                "task_type": self.plan.task_type,
                "target": self.plan.target,
                "steps": [
                    {
                        "id": step.id,
                        "name": step.name,
                        "command": step.command,
                        "risk": step.risk.value,
                        "required": step.required,
                        "tool_name": step.tool_name,
                        "tool_args": step.tool_args,
                    }
                    for step in self.plan.steps
                ],
            },
            "results": [result.to_dict() for result in self.results],
            "evidence": [item.to_dict() for item in self.evidence],
            "root_causes": self.root_causes,
            "suggestions": self.suggestions,
            "risk_level": self.risk_level,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "markdown_path": self.markdown_path,
            "json_path": self.json_path,
        }
