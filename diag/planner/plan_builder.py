from __future__ import annotations

from diag.core.models import DiagnosisPlan
from diag.planner.intent import infer_task
from diag.planner.templates import get_runbook
from diag.tools.registry import ToolRegistry


def build_plan(
    user_input: str | None,
    target: str,
    task: str | None = None,
    registry: ToolRegistry | None = None,
    service: str = "nginx",
) -> DiagnosisPlan:
    task_type = infer_task(user_input, task)
    return DiagnosisPlan(task_type=task_type, target=target, steps=get_runbook(task_type, registry=registry, service=service))
