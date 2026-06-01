from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_report_pane(state: WorkbenchState) -> str:
    lines = ["ReportPane"]
    report = state.outcome_report_path or state.dashboard.report_path
    json_path = state.outcome_json_path or state.dashboard.json_path
    lines.append(f"- Markdown: {report or 'pending'}")
    lines.append(f"- JSON: {json_path or 'pending'}")
    return "\n".join(lines)
