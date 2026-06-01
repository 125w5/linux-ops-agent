from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ResourceUsage:
    commands_started: int = 0
    commands_executed: int = 0
    commands_skipped: int = 0
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    total_output_bytes: int = 0
    truncated_results: int = 0
    ai_calls: int = 0
    duration_ms: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)
