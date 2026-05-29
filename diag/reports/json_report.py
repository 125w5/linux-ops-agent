from __future__ import annotations

import json
from pathlib import Path

from diag.core.models import DiagnosisOutcome


def write_json_report(outcome: DiagnosisOutcome, report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{outcome.session_id}.json"
    path.write_text(json.dumps(outcome.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path
