from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalRequest:
    command: str
    reason: str


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    reason: str


class ApprovalProvider:
    def request(self, request: ApprovalRequest) -> ApprovalDecision:
        return ApprovalDecision(False, f"Confirmation required: {request.reason}")


class StaticApprovalProvider(ApprovalProvider):
    def __init__(self, approved: bool, reason: str | None = None) -> None:
        self.approved = approved
        self.reason = reason or ("Approved by user" if approved else "Denied by user")

    def request(self, request: ApprovalRequest) -> ApprovalDecision:
        return ApprovalDecision(self.approved, self.reason)
