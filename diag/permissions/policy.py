from __future__ import annotations

from dataclasses import dataclass

from diag.core.models import RiskLevel
from diag.permissions.approval import ApprovalProvider, ApprovalRequest
from diag.permissions.mode import PermissionMode
from diag.permissions.sandbox_profiles import evaluate_sandbox
from diag.safety.command_checker import SafetyDecision, check_command


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    risk_level: RiskLevel
    reason: str
    requires_confirmation: bool = False


class PermissionPolicy:
    def __init__(self, mode: PermissionMode, approval_provider: ApprovalProvider | None = None, sandbox_profile: str = "safe-read") -> None:
        self.mode = mode
        self.approval_provider = approval_provider or ApprovalProvider()
        self.sandbox_profile = sandbox_profile

    def evaluate(self, command: str, preset_risk: RiskLevel | None = None) -> PermissionDecision:
        safety: SafetyDecision = check_command(command)
        if self.mode == PermissionMode.BLOCKED:
            return PermissionDecision(False, RiskLevel.BLOCKED, "Permission mode is blocked")
        if not safety.allowed:
            return PermissionDecision(False, safety.risk_level, safety.reason)
        risk_level = preset_risk or safety.risk_level
        sandbox = evaluate_sandbox(self.sandbox_profile, command, risk_level)
        reason = sandbox.reason
        if sandbox.action == "deny":
            return PermissionDecision(False, risk_level, reason)
        if sandbox.action == "ask" or (risk_level == RiskLevel.LOW_RISK and self.mode == PermissionMode.CONFIRM):
            approval = self.approval_provider.request(ApprovalRequest(command, reason))
            return PermissionDecision(approval.approved, risk_level, approval.reason, requires_confirmation=True)
        return PermissionDecision(True, risk_level, reason)
