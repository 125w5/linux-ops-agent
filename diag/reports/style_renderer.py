from __future__ import annotations

import json

from diag.core.models import DiagnosisOutcome
from diag.ui.theme import load_output_style


def render_report(outcome: DiagnosisOutcome, style: str | None = None) -> tuple[str, str]:
    output_style = load_output_style(style)
    if output_style.name == "json" or style == "json":
        return "json", json.dumps(outcome.to_dict(), indent=2, ensure_ascii=False) + "\n"

    title = output_style.title
    if output_style.name == "student":
        intro = "This report explains the diagnosis path, evidence, and conclusion for review."
    elif output_style.name == "security":
        intro = "Security-focused report: risk indicators, users, sources, and recommendations are highlighted."
    elif output_style.name == "minimal":
        intro = "Concise diagnosis report."
    else:
        intro = "Operations diagnosis report."

    lines = [
        f"# {title}: {outcome.task_type}",
        "",
        intro,
        "",
        f"- Session: `{outcome.session_id}`",
        f"- Target: `{outcome.target}`",
        f"- {output_style.risk_label}: `{outcome.risk_level}`",
        f"- Started: `{outcome.started_at}`",
        f"- Ended: `{outcome.ended_at}`",
        "",
        "## User Input",
        "",
        outcome.user_input or "(fixed task)",
        "",
        "## Diagnosis Plan",
        "",
    ]
    for index, step in enumerate(outcome.plan.steps, start=1):
        lines.append(f"{index}. {step.name}: `{step.command}` ({step.risk.value})")

    lines.extend(["", "## Command Results", ""])
    for result in outcome.results:
        status = "skipped" if result.skipped else str(result.return_code)
        truncated = " yes" if result.truncated else " no"
        lines.extend(
            [
                f"### `{result.command}`",
                "",
                f"- Return code: `{status}`",
                f"- Duration: `{result.duration_ms}ms`",
                f"- Truncated:{truncated}",
                "",
            ]
        )
        if result.stdout:
            lines.extend(["```text", result.stdout.strip()[:4000], "```", ""])
        if result.stderr:
            lines.extend(["stderr:", "", "```text", result.stderr.strip()[:2000], "```", ""])

    evidence_title = "Security Evidence" if output_style.name == "security" else "Evidence Chain"
    lines.extend([f"## {evidence_title}", ""])
    for item in outcome.evidence:
        lines.append(f"- [{item.severity}] {item.evidence_type} from `{item.source}`: {item.content}")

    lines.extend(["", "## Likely Root Causes", ""])
    lines.extend(f"- {cause}" for cause in outcome.root_causes)
    lines.extend(["", f"## {output_style.suggestions_label}", ""])
    lines.extend(f"- {suggestion}" for suggestion in outcome.suggestions)
    return "md", "\n".join(lines) + "\n"
