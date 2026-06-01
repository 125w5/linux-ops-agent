from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from diag.utils.paths import transcript_dir


def last_transcript_path() -> Path | None:
    paths = sorted(transcript_dir().glob("*.transcript.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return paths[0] if paths else None


def load_transcript(path: Path | None = None) -> dict[str, Any] | None:
    selected = path or last_transcript_path()
    if not selected:
        return None
    return json.loads(selected.read_text(encoding="utf-8"))


def render_session_summary(transcript: dict[str, Any]) -> str:
    lines = [f"session_id: {transcript.get('session_id')}"]
    for event in transcript.get("events", []):
        lines.append(f"- {event.get('type')} @ {event.get('timestamp')}")
    return "\n".join(lines)
