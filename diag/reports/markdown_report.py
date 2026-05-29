from __future__ import annotations

from pathlib import Path

from diag.core.models import DiagnosisOutcome


def write_markdown_report(outcome: DiagnosisOutcome, report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Diagnosis Report: {outcome.task_type}",
        "",
        f"- Session: `{outcome.session_id}`",
        f"- Target: `{outcome.target}`",
        f"- Risk level: `{outcome.risk_level}`",
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
        lines.extend(
            [
                f"### `{result.command}`",
                "",
                f"- Return code: `{status}`",
                f"- Duration: `{result.duration_ms}ms`",
                "",
            ]
        )
        if result.stdout:
            lines.extend(["```text", result.stdout.strip()[:4000], "```", ""])
        if result.stderr:
            lines.extend(["stderr:", "", "```text", result.stderr.strip()[:2000], "```", ""])

    lines.extend(["## Evidence Chain", ""])
    for item in outcome.evidence:
        lines.append(f"- [{item.severity}] {item.evidence_type} from `{item.source}`: {item.content}")

    lines.extend(["", "## Likely Root Causes", ""])
    for cause in outcome.root_causes:
        lines.append(f"- {cause}")

    lines.extend(["", "## Suggestions", ""])
    for suggestion in outcome.suggestions:
        lines.append(f"- {suggestion}")

    path = report_dir / f"{outcome.session_id}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
