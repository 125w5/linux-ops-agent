from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from diag.core.models import utc_now


@dataclass(frozen=True)
class RuntimeEvent:
    type: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=utc_now)
