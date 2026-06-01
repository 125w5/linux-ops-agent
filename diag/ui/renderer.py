from __future__ import annotations

import json
from typing import Any

from diag.core.models import DiagnosisOutcome
from diag.ui.cards import evidence_card, risk_card
from diag.ui.charts import cpu_bar, disk_bar
from diag.ui.raw_view import render_raw_results
from diag.ui.theme import load_output_style
from diag.ui.tree import render_plan_tree


def _quiet_summary(outcome: DiagnosisOutcome, resources: dict[str, Any] | None) -> str:
    return json.dumps(
        {
            "session_id": outcome.session_id,
            "task": outcome.task_type,
            "target": outcome.target,
            "risk": outcome.risk_level,
            "report_path": outcome.markdown_path,
            "commands": len(outcome.results),
            "truncated_results": (resources or {}).get("truncated_results", 0),
        },
        ensure_ascii=False,
    )


def _fact_json(outcome: DiagnosisOutcome, resources: dict[str, Any] | None) -> str:
    return json.dumps(
        {
            "session_id": outcome.session_id,
            "task": outcome.task_type,
            "target": outcome.target,
            "risk": outcome.risk_level,
            "report_path": outcome.markdown_path,
            "evidence": [item.to_dict() for item in outcome.evidence],
            "root_causes": outcome.root_causes,
            "suggestions": outcome.suggestions,
            "resources": resources or {},
        },
        ensure_ascii=False,
    )


def _chart_lines(outcome: DiagnosisOutcome) -> list[str]:
    lines: list[str] = []
    for item in outcome.evidence:
        if outcome.task_type == "disk" and "usage is" in item.content:
            try:
                percent = float(item.content.rsplit(" ", 1)[-1].rstrip("%"))
            except ValueError:
                continue
            lines.append(disk_bar("disk", percent))
        if outcome.task_type == "cpu" and item.evidence_type == "cpu_snapshot":
            tokens = item.content.replace("%", " %").split()
            if len(tokens) > 2 and tokens[0].isalpha() and tokens[1].isdigit():
                tokens = tokens[2:]
            for token in tokens:
                try:
                    percent = float(token)
                except ValueError:
                    continue
                if percent > 100:
                    continue
                lines.append(cpu_bar("cpu", percent))
                break
    return lines


def render_outcome(outcome: DiagnosisOutcome, view: str = "normal", style: str | None = None, resources: dict[str, Any] | None = None) -> str:
    if view == "plain":
        view = "normal"
    output_style = load_output_style(style)
    if output_style.name == "json" or style == "json" or view == "json":
        return _fact_json(outcome, resources)

    if view == "quiet":
        return _quiet_summary(outcome, resources)

    lines = [output_style.title, f"{output_style.risk_label}: {outcome.risk_level}", risk_card(outcome.risk_level)]
    if view in {"compact", "normal", "verbose", "raw"}:
        lines.append("Likely root causes:")
        lines.extend(f"- {cause}" for cause in outcome.root_causes)
        lines.append(output_style.suggestions_label + ":")
        lines.extend(f"- {suggestion}" for suggestion in outcome.suggestions)
        if outcome.markdown_path:
            lines.append(f"Report: {outcome.markdown_path}")

    if view in {"normal", "verbose", "raw"}:
        chart_lines = _chart_lines(outcome)
        if chart_lines:
            lines.append("")
            lines.append("Quick View:")
            lines.extend(chart_lines)
        lines.append("")
        lines.append("Evidence Chain:")
        lines.extend(f"- [{item.severity}] {item.content}" for item in outcome.evidence[:5])

    if view in {"verbose", "raw"}:
        lines.append("")
        lines.append(render_plan_tree(outcome.plan))
        lines.append("")
        lines.append("Evidence Cards:")
        lines.extend(evidence_card(item) for item in outcome.evidence)
        lines.append("")
        lines.append("Tool Calls:")
        for step, result in zip(outcome.plan.steps, outcome.results):
            tool = step.tool_name or step.id
            status = "skipped" if result.skipped else "ok" if result.return_code == 0 else f"rc={result.return_code}"
            truncated = " truncated" if result.truncated else ""
            lines.append(f"- {tool}: `{result.command}` -> {status}{truncated}")
        if resources:
            lines.append("")
            lines.append("Resources:")
            for key, value in resources.items():
                lines.append(f"- {key}: {value}")

    if view == "raw":
        lines.append("")
        lines.append("Raw command output:")
        lines.append(render_raw_results(outcome.results))
    return "\n".join(lines)
