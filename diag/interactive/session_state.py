from __future__ import annotations

from dataclasses import dataclass, field

from diag.core.models import DiagnosisOutcome, DiagnosisPlan
from diag.permissions.mode import PermissionMode


@dataclass
class InteractiveSessionState:
    target: str
    mode: PermissionMode
    service: str = "nginx"
    provider: str | None = None
    model: str | None = None
    profile: str | None = None
    style: str | None = None
    skill: str | None = None
    user_input: str = ""
    task_type: str | None = None
    plan: DiagnosisPlan | None = None
    outcome: DiagnosisOutcome | None = None
    status: str = "planning"
    pending_command: str | None = None
    resource_usage: dict[str, int] = field(default_factory=dict)

    def describe(self) -> str:
        task = self.task_type or "(none)"
        plan_steps = len(self.plan.steps) if self.plan else 0
        session_id = self.outcome.session_id if self.outcome else "(not-run)"
        return (
            f"status={self.status} task={task} target={self.target} mode={self.mode.value} "
            f"steps={plan_steps} session={session_id}"
        )
