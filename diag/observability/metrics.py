from __future__ import annotations

from typing import Any


def metrics_from_transcript(transcript: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {"session_id": transcript.get("session_id")}
    for event in transcript.get("events", []):
        if event.get("type") == "resource_usage":
            metrics.update(event.get("payload", {}))
        if event.get("type") == "plan":
            metrics["commands_count"] = len(event.get("payload", {}).get("steps", []))
    return metrics


def render_metrics(metrics: dict[str, Any]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in metrics.items())
