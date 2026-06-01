from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_evidence_pane(state: WorkbenchState) -> str:
    lines = ["EvidencePane"]
    if not state.dashboard.evidence:
        lines.append("- waiting for evidence")
    for item in state.dashboard.evidence[-8:]:
        lines.append(f"- [{item.get('severity', 'info')}] {item.get('content', '')}")
    return "\n".join(lines)
