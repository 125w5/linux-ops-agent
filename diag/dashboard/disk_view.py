from __future__ import annotations

from typing import Any


def disk_line(snapshot: dict[str, Any]) -> str:
    disk = snapshot.get("disk") or {}
    if not disk:
        return "Disk n/a"
    mount = disk.get("mountpoint", "/")
    used = disk.get("used_gb")
    total = disk.get("total_gb")
    percent = disk.get("percent")
    if used is None or total is None or percent is None:
        return f"Disk {mount} n/a"
    return f"Disk {mount} {used:.1f}/{total:.1f}GB {percent:.1f}%"
