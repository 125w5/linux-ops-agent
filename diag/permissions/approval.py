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
