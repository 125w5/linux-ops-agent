from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TuiEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


SESSION_STARTED = "SessionStarted"
PLAN_CREATED = "PlanCreated"
TOOL_STARTED = "ToolStarted"
TOOL_FINISHED = "ToolFinished"
EVIDENCE_ADDED = "EvidenceAdded"
APPROVAL_REQUIRED = "ApprovalRequired"
APPROVAL_RESOLVED = "ApprovalResolved"
REPORT_WRITTEN = "ReportWritten"
RESOURCE_UPDATED = "ResourceUpdated"
SESSION_ENDED = "SessionEnded"
