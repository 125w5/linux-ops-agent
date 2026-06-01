from __future__ import annotations

from typing import Any


def render_audit(transcript: dict[str, Any]) -> str:
    lines = [f"Audit for session {transcript.get('session_id')}"]
    for event in transcript.get("events", []):
        event_type = event.get("type")
        payload = event.get("payload", {})
        if event_type in {"before_command", "command_result", "resource_usage", "report_path"}:
            lines.append(f"- {event_type}: {payload}")
    return "\n".join(lines)
