from __future__ import annotations

import sqlite3
from pathlib import Path

from diag.core.models import DiagnosisOutcome


SCHEMA = """
CREATE TABLE IF NOT EXISTS diagnosis_sessions (
    id TEXT PRIMARY KEY,
    user_input TEXT,
    target TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT NOT NULL,
    markdown_path TEXT,
    json_path TEXT
);

CREATE TABLE IF NOT EXISTS command_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    command TEXT NOT NULL,
    stdout TEXT,
    stderr TEXT,
    return_code INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    executed_at TEXT NOT NULL,
    skipped INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS evidence_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    source TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    content TEXT NOT NULL,
    severity TEXT NOT NULL
);
"""


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def save(self, outcome: DiagnosisOutcome) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO diagnosis_sessions
                (id, user_input, target, task_type, status, started_at, ended_at, markdown_path, json_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    outcome.session_id,
                    outcome.user_input,
                    outcome.target,
                    outcome.task_type,
                    "completed",
                    outcome.started_at,
                    outcome.ended_at,
                    outcome.markdown_path,
                    outcome.json_path,
                ),
            )
            for result in outcome.results:
                conn.execute(
                    """
                    INSERT INTO command_results
                    (session_id, command, stdout, stderr, return_code, duration_ms, risk_level, executed_at, skipped)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        outcome.session_id,
                        result.command,
                        result.stdout,
                        result.stderr,
                        result.return_code,
                        result.duration_ms,
                        result.risk_level,
                        result.executed_at,
                        1 if result.skipped else 0,
                    ),
                )
            for item in outcome.evidence:
                conn.execute(
                    """
                    INSERT INTO evidence_items (session_id, source, evidence_type, content, severity)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (outcome.session_id, item.source, item.evidence_type, item.content, item.severity),
                )

    def list_sessions(self, limit: int = 10) -> list[tuple[str, str, str, str, str | None]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, task_type, target, ended_at, markdown_path
                FROM diagnosis_sessions
                ORDER BY ended_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return rows

    def last_report_path(self) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT markdown_path
                FROM diagnosis_sessions
                WHERE markdown_path IS NOT NULL
                ORDER BY ended_at DESC
                LIMIT 1
                """
            ).fetchone()
        return row[0] if row else None
