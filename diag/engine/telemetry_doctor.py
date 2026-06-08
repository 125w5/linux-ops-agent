from __future__ import annotations

import platform
import sys
import time
from typing import Any

from diag.engine.resource_schema import resource_event_payload, schema_status


def telemetry_doctor(snapshot: dict[str, Any] | None, *, frontend_received: bool = False) -> dict[str, Any]:
    source = snapshot or {}
    payload = resource_event_payload(source)
    schema = schema_status(payload)
    timestamp = payload.get("timestamp")
    sample_age_ms = None
    if isinstance(timestamp, (int, float)) and timestamp > 0:
        sample_age_ms = int((time.time() - float(timestamp)) * 1000)
    lines = [
        f"platform: {platform.platform()}",
        f"python: {sys.version.split()[0]}",
        f"python executable: {sys.executable}",
        f"psutil available: {payload.get('psutil_available')}",
        f"logical cpu count: {payload.get('logical_cpu_count')}",
        f"sampler status: {payload.get('sampler_status')}",
        f"sampler error: {payload.get('sampler_error') or 'none'}",
        f"last sample age: {sample_age_ms if sample_age_ms is not None else 'unknown'}ms",
        f"system cpu: {payload.get('system_cpu_percent')}",
        f"memory: {_memory_line(payload.get('memory'))}",
        f"disk: {_disk_line(payload.get('disk'))}",
        f"top cpu count: {len(payload.get('top_cpu') or [])}",
        f"top memory count: {len(payload.get('top_memory') or [])}",
        f"frontend received ResourceUpdated: {'yes' if frontend_received else 'no'}",
        f"schema validation: {'ok' if schema['ok'] else '; '.join(schema['errors'])}",
    ]
    return {
        "text": "\n".join(lines),
        "doctor": {
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
            "psutil_available": payload.get("psutil_available"),
            "logical_cpu_count": payload.get("logical_cpu_count"),
            "sampler_status": payload.get("sampler_status"),
            "sampler_error": payload.get("sampler_error"),
            "last_sample_age_ms": sample_age_ms,
            "system_cpu_percent": payload.get("system_cpu_percent"),
            "memory": payload.get("memory"),
            "disk": payload.get("disk"),
            "top_cpu_count": len(payload.get("top_cpu") or []),
            "top_memory_count": len(payload.get("top_memory") or []),
            "frontend_received_resource_updated": frontend_received,
            "schema": schema,
        },
    }


def _memory_line(value: Any) -> str:
    memory = value if isinstance(value, dict) else {}
    return f"{memory.get('used_bytes', 0)} / {memory.get('total_bytes', 0)} bytes ({memory.get('percent')})"


def _disk_line(value: Any) -> str:
    disk = value if isinstance(value, dict) else {}
    return f"{disk.get('mount', '')} {disk.get('used_bytes', 0)} / {disk.get('total_bytes', 0)} bytes ({disk.get('percent')})"
