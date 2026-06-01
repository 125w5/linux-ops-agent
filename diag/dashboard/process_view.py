from __future__ import annotations

from typing import Any


def compact_processes(processes: list[dict[str, Any]], metric: str, limit: int = 3) -> str:
    if not processes:
        return "n/a"
    rows = []
    for proc in processes[:limit]:
        name = str(proc.get("name") or proc.get("command") or "?")
        value = proc.get(metric, 0)
        suffix = ""
        if metric == "memory_percent" and not value and proc.get("memory_mb") is not None:
            value = proc.get("memory_mb")
            suffix = "MB"
        try:
            rendered_value = f"{float(value):.1f}{suffix}"
        except (TypeError, ValueError):
            rendered_value = str(value)
        rows.append(f"{name}:{rendered_value}")
    return ", ".join(rows)
