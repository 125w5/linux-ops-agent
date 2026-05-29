from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def report_dir() -> Path:
    return project_root() / "outputs" / "reports"


def database_path() -> Path:
    return project_root() / "outputs" / "history" / "diag.db"


def transcript_dir() -> Path:
    return project_root() / "outputs" / "history" / "transcripts"
