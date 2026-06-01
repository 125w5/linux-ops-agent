from __future__ import annotations

from diag.dashboard.renderers import _resource_details, _resource_line
from diag.workbench.state import WorkbenchState


def render_monitor_pane(state: WorkbenchState) -> str:
    resources = state.dashboard.resources
    return "\n".join(["MonitorPane", _resource_line(resources), *_resource_details(resources)[:3]])
