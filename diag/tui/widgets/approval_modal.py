from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalModal:
    command: str
    risk: str
    reason: str

    def render(self) -> str:
        if self.risk == "blocked":
            return f"Blocked command\n{self.command}\nReason: {self.reason}\nApproval is not available."
        return f"Pending Command\n{self.command}\nRisk: {self.risk}\nA=/approve D=/deny\nReason: {self.reason}"
