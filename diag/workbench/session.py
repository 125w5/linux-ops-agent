from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from diag.core.models import utc_now
from diag.utils.paths import transcript_dir
from diag.workbench.message import WorkbenchMessage


class WorkbenchSession:
    def __init__(self, session_id: str | None = None) -> None:
        self.session_id = session_id or str(uuid4())
        self.started_at = utc_now()
        self.ended_at: str | None = None
        self.events: list[dict] = []

    def append_message(self, message: WorkbenchMessage) -> None:
        self.events.append({"type": "message", "payload": message.to_dict(), "timestamp": utc_now()})

    def append_event(self, event_type: str, payload: dict) -> None:
        self.events.append({"type": event_type, "payload": payload, "timestamp": utc_now()})

    def close(self) -> None:
        self.ended_at = utc_now()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "events": self.events,
        }

    def write(self, directory: Path | None = None) -> Path:
        target_dir = directory or (transcript_dir() / "workbench")
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{self.session_id}.workbench.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path
