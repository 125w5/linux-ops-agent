from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from diag.core.models import utc_now


@dataclass
class WorkbenchMessage:
    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
