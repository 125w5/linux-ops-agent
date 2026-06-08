from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


TRACE_FIELDS = (
    "input_received_ms",
    "placeholder_painted_ms",
    "fast_router_ms",
    "local_plan_ms",
    "api_call_count",
    "api_call_start_ms",
    "api_first_token_ms",
    "api_total_ms",
    "tool_run_ms",
    "local_summary_ms",
    "report_write_ms",
    "total_turn_ms",
    "fallback_reason",
)


@dataclass
class LatencyTrace:
    started: float = field(default_factory=time.perf_counter)
    input_received_ms: int = 0
    placeholder_painted_ms: int = 0
    fast_router_ms: int = 0
    local_plan_ms: int = 0
    api_call_count: int = 0
    api_call_start_ms: int = 0
    api_first_token_ms: int = 0
    api_total_ms: int = 0
    tool_run_ms: int = 0
    local_summary_ms: int = 0
    report_write_ms: int = 0
    total_turn_ms: int = 0
    fallback_reason: str = ""

    def mark_total(self) -> None:
        self.total_turn_ms = self.elapsed()

    def elapsed(self) -> int:
        return int((time.perf_counter() - self.started) * 1000)

    def to_dict(self) -> dict[str, Any]:
        self.mark_total()
        return {field: getattr(self, field) for field in TRACE_FIELDS}


def empty_latency_trace() -> dict[str, Any]:
    return {field: "" if field == "fallback_reason" else 0 for field in TRACE_FIELDS}
