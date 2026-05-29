from __future__ import annotations

from dataclasses import dataclass

from diag.permissions.mode import PermissionMode


@dataclass(frozen=True)
class SandboxPolicy:
    mode: PermissionMode

    @property
    def allows_execution(self) -> bool:
        return self.mode in {PermissionMode.DEMO, PermissionMode.READONLY, PermissionMode.CONFIRM, PermissionMode.FAULT_LAB}

    @property
    def is_demo(self) -> bool:
        return self.mode == PermissionMode.DEMO

    def describe(self) -> str:
        if self.mode == PermissionMode.DEMO:
            return "demo replay"
        if self.mode == PermissionMode.FAULT_LAB:
            return "fault lab read-only collection"
        if self.mode == PermissionMode.CONFIRM:
            return "confirm before low-risk operations"
        if self.mode == PermissionMode.BLOCKED:
            return "blocked"
        return "readonly"
