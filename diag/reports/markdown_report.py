from __future__ import annotations

from pathlib import Path

from diag.core.models import DiagnosisOutcome
from diag.reports.style_renderer import render_report


def write_markdown_report(outcome: DiagnosisOutcome, report_dir: Path, style: str | None = None) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    kind, content = render_report(outcome, style)
    suffix = ".json" if kind == "json" else ".md"
    path = report_dir / f"{outcome.session_id}{suffix}"
    path.write_text(content, encoding="utf-8")
    return path
