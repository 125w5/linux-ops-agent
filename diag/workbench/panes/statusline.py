from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_statusline(state: WorkbenchState) -> str:
    session = state.dashboard.session_id[:8] if state.dashboard.session_id else "workbench"
    model = state.model or "default"
    return (
        f"OpsPilot-Linux | session={session} | target={state.target} | task={state.task_type} | "
        f"mode={state.mode.value} | risk={state.risk} | model={model} | status={state.status}"
    )
