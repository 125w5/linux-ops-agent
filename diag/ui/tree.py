from __future__ import annotations

from diag.core.models import DiagnosisPlan


def render_plan_tree(plan: DiagnosisPlan) -> str:
    lines = [f"PlanTree: {plan.task_type} -> {plan.target}"]
    for index, step in enumerate(plan.steps, start=1):
        connector = "`-" if index == len(plan.steps) else "|-"
        tool = f" [{step.tool_name}]" if step.tool_name else ""
        lines.append(f"  {connector} {step.name}{tool}")
    return "\n".join(lines)
