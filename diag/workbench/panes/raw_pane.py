from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_raw_pane(state: WorkbenchState) -> str:
    lines = ["RawPane"]
    if not state.raw_expanded:
        lines.append(f"- folded ({len(state.dashboard.raw_summary)} summaries); use /raw")
        return "\n".join(lines)
    lines.extend(f"- {item}" for item in (state.dashboard.raw_summary or ["no raw summary yet"]))
    return "\n".join(lines)
