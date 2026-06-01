from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkbenchOptions:
    target: str = "localhost"
    mode: str | None = "demo"
    task: str = "disk"
    service: str = "nginx"
    provider: str | None = None
    model: str | None = None
    profile: str | None = None
    style: str | None = None
    skill: str | None = None
    timeout: int = 15
    use_ssh: bool = False
    demo: bool = False
