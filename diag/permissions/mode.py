from __future__ import annotations

from enum import Enum


class PermissionMode(str, Enum):
    DEMO = "demo"
    READONLY = "readonly"
    CONFIRM = "confirm"
    FAULT_LAB = "fault-lab"
    BLOCKED = "blocked"


def parse_permission_mode(value: str | None, demo: bool = False) -> PermissionMode:
    if demo:
        return PermissionMode.DEMO
    if not value:
        return PermissionMode.READONLY
    return PermissionMode(value)
