from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_resources_pane(state: WorkbenchState) -> str:
    resources = state.dashboard.resources
    return "\n".join(
        [
            "ResourcesPane",
            f"- commands: started={resources.get('commands_started', 0)} executed={resources.get('commands_executed', 0)} skipped={resources.get('commands_skipped', 0)}",
            f"- stdout bytes: {resources.get('stdout_bytes', 0)}",
            f"- ai calls: {resources.get('ai_calls', 0)}",
            f"- render ms: {resources.get('render_ms', 0)}",
        ]
    )
