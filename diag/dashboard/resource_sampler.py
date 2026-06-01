from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def sample_resources() -> dict[str, Any]:
    try:
        return _sample_psutil()
    except Exception:
        return _sample_fallback()


def _sample_psutil() -> dict[str, Any]:
    import psutil  # type: ignore

    cpu_percent = float(psutil.cpu_percent(interval=None))
    load_avg = list(os.getloadavg()) if hasattr(os, "getloadavg") else []
    memory = psutil.virtual_memory()
    disk_path = _disk_sample_path()
    disk = psutil.disk_usage(disk_path)
    processes: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
        except Exception:
            continue
        processes.append(
            {
                "pid": info.get("pid"),
                "name": info.get("name") or "?",
                "cpu_percent": float(info.get("cpu_percent") or 0),
                "memory_percent": float(info.get("memory_percent") or 0),
            }
        )
    return {
        "system": {
            "cpu_percent": cpu_percent,
            "load_average": load_avg,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "memory_percent": float(memory.percent),
        },
        "disk": {
            "mountpoint": _display_mountpoint(disk_path),
            "used_gb": disk.used / (1024**3),
            "total_gb": disk.total / (1024**3),
            "percent": float(disk.percent),
        },
        "top_cpu_processes": sorted(processes, key=lambda item: item.get("cpu_percent", 0), reverse=True)[:5],
        "top_memory_processes": sorted(processes, key=lambda item: item.get("memory_percent", 0), reverse=True)[:5],
    }


def _sample_fallback() -> dict[str, Any]:
    return {
        "system": _fallback_system(),
        "disk": _fallback_disk(),
        "top_cpu_processes": _fallback_processes("-pcpu"),
        "top_memory_processes": _fallback_processes("-pmem"),
    }


def _fallback_system() -> dict[str, Any]:
    if os.name == "nt":
        return _windows_system()
    load_avg = list(os.getloadavg()) if hasattr(os, "getloadavg") else []
    memory = _read_meminfo()
    cpu_percent = _read_proc_stat_cpu_percent()
    return {
        "cpu_percent": cpu_percent,
        "load_average": load_avg,
        "memory_used_gb": memory.get("used_gb"),
        "memory_total_gb": memory.get("total_gb"),
        "memory_percent": memory.get("percent"),
    }


def _read_meminfo() -> dict[str, float | None]:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        values: dict[str, float] = {}
        for line in meminfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            parts = line.split()
            if len(parts) >= 2:
                values[parts[0].rstrip(":")] = float(parts[1])
        total = values.get("MemTotal")
        available = values.get("MemAvailable", values.get("MemFree"))
        if total and available is not None:
            used = total - available
            return {
                "used_gb": used / 1024 / 1024,
                "total_gb": total / 1024 / 1024,
                "percent": used / total * 100,
            }

    output = _run(["free", "-b"])
    if output:
        for line in output.splitlines():
            if line.lower().startswith("mem:"):
                parts = line.split()
                if len(parts) >= 3:
                    total = float(parts[1])
                    used = float(parts[2])
                    return {"used_gb": used / (1024**3), "total_gb": total / (1024**3), "percent": used / total * 100}
    return {"used_gb": None, "total_gb": None, "percent": None}


def _read_proc_stat_cpu_percent() -> float | None:
    stat = Path("/proc/stat")
    if not stat.exists():
        return None
    first = stat.read_text(encoding="utf-8", errors="ignore").splitlines()[0].split()[1:]
    values = [float(item) for item in first]
    total = sum(values)
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    if total <= 0:
        return None
    return max(0.0, min(100.0, 100.0 - idle / total * 100.0))


def _fallback_disk() -> dict[str, Any]:
    disk_path = _disk_sample_path()
    usage = shutil.disk_usage(disk_path)
    return {
        "mountpoint": _display_mountpoint(disk_path),
        "used_gb": usage.used / (1024**3),
        "total_gb": usage.total / (1024**3),
        "percent": usage.used / usage.total * 100 if usage.total else None,
    }


def _disk_sample_path() -> str:
    if os.name == "nt":
        return Path.cwd().anchor or os.path.abspath(os.sep)
    return "/"


def _display_mountpoint(path: str) -> str:
    if os.name == "nt":
        drive = Path(path).anchor.rstrip("\\/")
        return drive or path
    return path


def _fallback_processes(sort_key: str) -> list[dict[str, Any]]:
    if os.name == "nt":
        return _windows_processes(sort_key)
    output = _run(["ps", "-eo", "pid,comm,pcpu,pmem", f"--sort={sort_key}"])
    rows: list[dict[str, Any]] = []
    if not output:
        return rows
    for line in output.splitlines()[1:6]:
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        pid, name, cpu, mem = parts
        try:
            rows.append({"pid": int(pid), "name": name, "cpu_percent": float(cpu), "memory_percent": float(mem)})
        except ValueError:
            continue
    return rows


def _run(args: list[str]) -> str:
    try:
        completed = subprocess.run(args, text=True, capture_output=True, timeout=2, check=False)
    except Exception:
        return ""
    return completed.stdout


def _windows_system() -> dict[str, Any]:
    memory = _windows_memory()
    cpu_percent = _windows_cpu_percent()
    return {
        "cpu_percent": cpu_percent,
        "load_average": [],
        "memory_used_gb": memory.get("used_gb"),
        "memory_total_gb": memory.get("total_gb"),
        "memory_percent": memory.get("percent"),
    }


def _windows_memory() -> dict[str, float | None]:
    try:
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            total = float(status.ullTotalPhys)
            used = total - float(status.ullAvailPhys)
            return {"used_gb": used / (1024**3), "total_gb": total / (1024**3), "percent": float(status.dwMemoryLoad)}
    except Exception:
        pass
    return {"used_gb": None, "total_gb": None, "percent": None}


def _windows_cpu_percent() -> float | None:
    output = _run(["wmic", "cpu", "get", "loadpercentage", "/value"])
    values = []
    for line in output.splitlines():
        if line.lower().startswith("loadpercentage="):
            try:
                values.append(float(line.split("=", 1)[1]))
            except ValueError:
                continue
    if values:
        return sum(values) / len(values)
    return None


def _windows_processes(sort_key: str) -> list[dict[str, Any]]:
    sort_property = "WorkingSet64" if "mem" in sort_key.lower() else "CPU"
    command = (
        "Get-Process | Sort-Object "
        f"{sort_property} -Descending | Select-Object -First 5 Id,ProcessName,CPU,WorkingSet64 | ConvertTo-Json"
    )
    output = _run(["powershell", "-NoProfile", "-Command", command])
    if not output.strip():
        return []
    try:
        import json

        data = json.loads(output)
    except Exception:
        return []
    rows = data if isinstance(data, list) else [data]
    processes: list[dict[str, Any]] = []
    for row in rows:
        working_set = float(row.get("WorkingSet64") or 0)
        processes.append(
            {
                "pid": row.get("Id"),
                "name": row.get("ProcessName") or "?",
                "cpu_percent": float(row.get("CPU") or 0),
                "memory_percent": 0.0,
                "memory_mb": working_set / (1024**2),
            }
        )
    return processes
