from __future__ import annotations

from pathlib import Path

from diag.tui.pagination import preview_bytes, tail_lines
from diag.tui.state import TuiState


def render_status_bar(state: TuiState) -> str:
    return f"StatusBar | session={state.session_id or '-'} target={state.target} mode={state.mode} status={state.status}"


def render_plan_pane(state: TuiState) -> str:
    lines = ["PlanPane"]
    if not state.plan:
        lines.append("(no plan)")
    for index, step in enumerate(state.plan, start=1):
        tool = f" [{step.get('tool_name')}]" if step.get("tool_name") else ""
        lines.append(f"{index}. {step.get('name', step.get('id', 'step'))}{tool}")
    return "\n".join(lines)


def render_evidence_pane(state: TuiState) -> str:
    lines = ["EvidencePane"]
    if not state.evidence:
        lines.append("(no evidence)")
    for item in state.evidence[:20]:
        lines.append(f"- [{item.get('severity', 'info')}] {item.get('content', '')}")
    if len(state.evidence) > 20:
        lines.append("[truncated]")
    return "\n".join(lines)


def render_raw_pane(state: TuiState, expanded: bool = False) -> str:
    lines = ["RawPane"]
    if not state.raw:
        lines.append("(no raw output)")
        return "\n".join(lines)
    if not expanded:
        lines.append(f"{len(state.raw)} raw event(s). Press F2 to expand.")
        return "\n".join(lines)
    page = tail_lines(state.raw, 200)
    lines.append(page.text)
    if page.truncated:
        lines.append("[truncated]")
    return "\n".join(lines)


def render_report_pane(state: TuiState) -> str:
    lines = ["ReportPane"]
    if not state.report_path:
        lines.append("(no report)")
        return "\n".join(lines)
    path = Path(state.report_path)
    lines.append(str(path))
    if path.exists():
        page = preview_bytes(path.read_text(encoding="utf-8"), 100 * 1024)
        lines.append(page.text)
    return "\n".join(lines)


def render_resources_pane(state: TuiState) -> str:
    lines = ["ResourcesPane"]
    if not state.resources:
        lines.append("(no resource usage)")
    lines.extend(f"- {key}: {value}" for key, value in state.resources.items())
    return "\n".join(lines)


def render_plugin_pane(_: TuiState) -> str:
    return "PluginPane\nUse /plugin or `diag plugin list`."


def render_model_pane(_: TuiState) -> str:
    return "ModelPane\nUse /model or `diag model doctor`."


def render_command_input(_: TuiState) -> str:
    return "CommandInput\nPress / for command palette."


PANE_RENDERERS = {
    "StatusBar": render_status_bar,
    "PlanPane": render_plan_pane,
    "EvidencePane": render_evidence_pane,
    "RawPane": render_raw_pane,
    "ReportPane": render_report_pane,
    "ResourcesPane": render_resources_pane,
    "PluginPane": render_plugin_pane,
    "ModelPane": render_model_pane,
    "CommandInput": render_command_input,
}


def render_pane(name: str, state: TuiState) -> str:
    renderer = PANE_RENDERERS.get(name)
    if not renderer:
        return f"{name}\n(unavailable)"
    return renderer(state)
