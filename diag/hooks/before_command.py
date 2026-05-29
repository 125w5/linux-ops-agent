from __future__ import annotations

from diag.core.models import DiagnosisStep
from diag.permissions.policy import PermissionDecision
from diag.runtime.context import RuntimeContext


class BeforeCommandSafetyHook:
    def __call__(self, context: RuntimeContext, step: DiagnosisStep) -> PermissionDecision:
        decision = context.permission_policy.evaluate(step.command)
        context.transcript.append_event(
            "before_command",
            {
                "step_id": step.id,
                "command": step.command,
                "allowed": decision.allowed,
                "risk_level": decision.risk_level.value,
                "reason": decision.reason,
            },
        )
        return decision
