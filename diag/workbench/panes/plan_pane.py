from __future__ import annotations

from diag.dashboard.renderers import _tool_line
from diag.workbench.state import WorkbenchState


def render_plan_pane(state: WorkbenchState) -> str:
    lines = ["PlanPane"]
    if state.dashboard.tool_calls:
        lines.extend(_tool_line(call) for call in state.dashboard.tool_calls)
    elif state.current_plan:
        for step in state.current_plan.steps:
            lines.append(f"- [pending] {step.tool_name or step.id}: `{step.command}` risk={step.risk.value}")
    else:
        lines.append("- no plan yet")
    return "\n".join(lines)
