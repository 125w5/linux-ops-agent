from __future__ import annotations

from dataclasses import dataclass

from diag.core.models import RiskLevel
from diag.permissions.approval import ApprovalProvider, ApprovalRequest
from diag.permissions.mode import PermissionMode
from diag.safety.command_checker import SafetyDecision, check_command


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    risk_level: RiskLevel
    reason: str
    requires_confirmation: bool = False


class PermissionPolicy:
    def __init__(self, mode: PermissionMode, approval_provider: ApprovalProvider | None = None) -> None:
        self.mode = mode
        self.approval_provider = approval_provider or ApprovalProvider()

    def evaluate(self, command: str) -> PermissionDecision:
        safety: SafetyDecision = check_command(command)
        if self.mode == PermissionMode.BLOCKED:
            return PermissionDecision(False, RiskLevel.BLOCKED, "Permission mode is blocked")
        if not safety.allowed:
            return PermissionDecision(False, safety.risk_level, safety.reason)
        if safety.risk_level == RiskLevel.LOW_RISK and self.mode == PermissionMode.CONFIRM:
            approval = self.approval_provider.request(ApprovalRequest(command, safety.reason))
            return PermissionDecision(approval.approved, safety.risk_level, approval.reason, requires_confirmation=True)
        if safety.risk_level == RiskLevel.LOW_RISK:
            return PermissionDecision(False, safety.risk_level, "Low-risk commands require confirm mode")
        return PermissionDecision(True, safety.risk_level, safety.reason)
