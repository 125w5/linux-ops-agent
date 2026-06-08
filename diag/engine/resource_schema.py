from __future__ import annotations

import platform
import time
from typing import Any


REQUIRED_RESOURCE_FIELDS = (
    "event",
    "timestamp",
    "sampler_status",
    "platform",
    "logical_cpu_count",
    "system_cpu_percent",
    "memory",
    "disk",
    "top_cpu",
    "top_memory",
)


def resource_event_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    system = _dict(snapshot.get("system"))
    disk = _dict(snapshot.get("disk"))
    logical_cpu_count = _number(snapshot.get("logical_cpu_count"), system.get("logical_cpu_count"), 1)
    memory_total = _number(system.get("memory_total_bytes"), _gb_to_bytes(system.get("memory_total_gb")))
    memory_used = _number(system.get("memory_bytes"), _gb_to_bytes(system.get("memory_used_gb")))
    disk_total = _number(disk.get("total_bytes"), _gb_to_bytes(disk.get("total_gb")))
    disk_used = _number(disk.get("used_bytes"), _gb_to_bytes(disk.get("used_gb")))
    payload = {
        "event": "ResourceUpdated",
        "timestamp": float(snapshot.get("timestamp") or time.time()),
        "sampler_status": str(snapshot.get("sampler_status") or system.get("sampler_status") or "error"),
        "sampler_error": snapshot.get("sampler_error") or snapshot.get("error") or system.get("sampler_error"),
        "platform": str(snapshot.get("platform") or platform.platform()),
        "python_version": str(snapshot.get("python_version") or platform.python_version()),
        "python_executable": str(snapshot.get("python_executable") or ""),
        "psutil_available": bool(snapshot.get("psutil_available", False)),
        "logical_cpu_count": int(logical_cpu_count or 1),
        "system_cpu_percent": _percent(snapshot.get("system_cpu_percent"), system.get("system_cpu_percent"), system.get("cpu_percent")),
        "memory": {
            "total_bytes": int(memory_total or 0),
            "used_bytes": int(memory_used or 0),
            "percent": _percent(system.get("memory_percent")),
        },
        "disk": {
            "mount": str(disk.get("mount") or disk.get("mountpoint") or disk.get("device") or ""),
            "total_bytes": int(disk_total or 0),
            "used_bytes": int(disk_used or 0),
            "percent": _percent(disk.get("percent"), disk.get("disk_percent")),
        },
        "top_cpu": [_process_row(row, int(logical_cpu_count or 1)) for row in _list(snapshot.get("top_cpu"), snapshot.get("top_cpu_processes"))[:3]],
        "top_memory": [_process_row(row, int(logical_cpu_count or 1)) for row in _list(snapshot.get("top_memory"), snapshot.get("top_memory_processes"))[:3]],
        "permission_denied_count": int(_number(snapshot.get("permission_denied_count"), 0) or 0),
        "sample_age_ms": int(_number(snapshot.get("sample_age_ms"), 0) or 0),
    }
    payload.update(_legacy_fields(payload, system))
    return payload


def validate_resource_event(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_RESOURCE_FIELDS:
        if key not in payload:
            errors.append(f"missing {key}")
    if _dict(payload.get("memory")).get("total_bytes") is None:
        errors.append("missing memory.total_bytes")
    if _dict(payload.get("disk")).get("total_bytes") is None:
        errors.append("missing disk.total_bytes")
    for key in ("top_cpu", "top_memory"):
        if key in payload and not isinstance(payload[key], list):
            errors.append(f"{key} must be list")
    return errors


def schema_status(payload: dict[str, Any]) -> dict[str, Any]:
    errors = validate_resource_event(payload)
    return {"ok": not errors, "errors": errors}


def _legacy_fields(payload: dict[str, Any], system: dict[str, Any]) -> dict[str, Any]:
    memory = _dict(payload.get("memory"))
    disk = _dict(payload.get("disk"))
    memory_total_gb = _bytes_to_gb(memory.get("total_bytes"))
    memory_used_gb = _bytes_to_gb(memory.get("used_bytes"))
    disk_total_gb = _bytes_to_gb(disk.get("total_bytes"))
    disk_used_gb = _bytes_to_gb(disk.get("used_bytes"))
    return {
        "system": {
            "cpu_percent": payload.get("system_cpu_percent"),
            "system_cpu_percent": payload.get("system_cpu_percent"),
            "logical_cpu_count": payload.get("logical_cpu_count"),
            "sampler_status": payload.get("sampler_status"),
            "sampler_error": payload.get("sampler_error"),
            "load_average": system.get("load_average") or [],
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
            "memory_bytes": memory.get("used_bytes"),
            "memory_total_bytes": memory.get("total_bytes"),
            "memory_percent": memory.get("percent"),
        },
        "top_cpu_processes": payload.get("top_cpu", []),
        "top_memory_processes": payload.get("top_memory", []),
        "schema": schema_status({key: payload.get(key) for key in REQUIRED_RESOURCE_FIELDS}),
    }


def _process_row(value: Any, logical_cpu_count: int) -> dict[str, Any]:
    row = _dict(value)
    raw_cpu = _number(row.get("raw_cpu_percent"), row.get("process_raw_cpu_percent"), row.get("cpu_percent"), 0) or 0.0
    normalized = _number(row.get("normalized_cpu_percent"), row.get("process_normalized_cpu_percent"))
    if normalized is None:
        normalized = raw_cpu / max(1, logical_cpu_count) if raw_cpu > 100 else raw_cpu
    return {
        "pid": row.get("pid"),
        "name": str(row.get("name") or "?"),
        "user": str(row.get("user") or row.get("username") or ""),
        "command": str(row.get("command") or row.get("cmdline") or ""),
        "raw_cpu_percent": float(raw_cpu),
        "normalized_cpu_percent": max(0.0, min(100.0, float(normalized))),
        "cpu_percent": max(0.0, min(100.0, float(normalized))),
        "memory_bytes": int(_number(row.get("memory_bytes"), _mb_to_bytes(row.get("memory_mb")), 0) or 0),
        "memory_percent": float(_number(row.get("memory_percent"), 0) or 0),
        "memory_mb": _number(row.get("memory_mb"), _bytes_to_mb(row.get("memory_bytes"))),
        "logical_cpu_count": logical_cpu_count,
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(*values: Any) -> list[Any]:
    for value in values:
        if isinstance(value, list):
            return value
    return []


def _number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _percent(*values: Any) -> float | None:
    value = _number(*values)
    if value is None:
        return None
    return max(0.0, min(100.0, value))


def _gb_to_bytes(value: Any) -> float | None:
    number = _number(value)
    return None if number is None else number * 1024 * 1024 * 1024


def _bytes_to_gb(value: Any) -> float | None:
    number = _number(value)
    return None if number is None else number / 1024 / 1024 / 1024


def _mb_to_bytes(value: Any) -> float | None:
    number = _number(value)
    return None if number is None else number * 1024 * 1024


def _bytes_to_mb(value: Any) -> float | None:
    number = _number(value)
    return None if number is None else number / 1024 / 1024
