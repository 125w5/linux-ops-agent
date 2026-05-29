from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from diag.core.models import utc_now
from diag.permissions.mode import PermissionMode


@dataclass
class RuntimeSession:
    user_input: str
    target: str
    task_type: str
    permission_mode: PermissionMode
    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=utc_now)
    ended_at: str | None = None

    def close(self) -> None:
        self.ended_at = utc_now()
