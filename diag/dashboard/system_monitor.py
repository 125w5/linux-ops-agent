from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

from diag.dashboard.resource_sampler import sample_resources


class SystemMonitor:
    def __init__(self, interval_seconds: float = 1.0, on_sample: Callable[[dict[str, Any]], None] | None = None) -> None:
        self.interval_seconds = max(0.5, interval_seconds)
        self.on_sample = on_sample
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_snapshot: dict[str, Any] = {}

    def sample_once(self) -> dict[str, Any]:
        try:
            snapshot = sample_resources()
        except Exception as exc:
            snapshot = {"system_monitor_error": str(exc)}
        self.last_snapshot = _stable_snapshot(snapshot)
        if self.on_sample:
            try:
                self.on_sample(self.last_snapshot)
            except Exception:
                pass
        return self.last_snapshot

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="opspilot-system-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval_seconds + 0.2)

    def _run(self) -> None:
        while not self._stop.is_set():
            self.sample_once()
            self._stop.wait(self.interval_seconds)

    def __enter__(self) -> "SystemMonitor":
        self.start()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.stop()


def _stable_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    system = snapshot.get("system")
    if isinstance(system, dict) and isinstance(system.get("cpu_percent"), (int, float)):
        system["cpu_percent"] = max(0.0, min(100.0, float(system["cpu_percent"])))
    return snapshot
