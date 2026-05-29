from __future__ import annotations

from diag.core.models import DiagnosisOutcome


def stage(index: int, total: int, message: str) -> None:
    print(f"[{index}/{total}] {message}")


def print_summary(outcome: DiagnosisOutcome) -> None:
    print("")
    print("Diagnosis complete")
    print(f"- Session: {outcome.session_id}")
    print(f"- Task: {outcome.task_type}")
    print(f"- Target: {outcome.target}")
    print(f"- Risk: {outcome.risk_level}")
    print("")
    print("Likely root causes:")
    for cause in outcome.root_causes:
        print(f"- {cause}")
    print("")
    print("Suggestions:")
    for suggestion in outcome.suggestions:
        print(f"- {suggestion}")
    if outcome.markdown_path:
        print("")
        print(f"Markdown report: {outcome.markdown_path}")
    if outcome.json_path:
        print(f"JSON report: {outcome.json_path}")
