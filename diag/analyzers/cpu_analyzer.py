from __future__ import annotations

import re

from diag.core.models import CommandResult, EvidenceItem


def _load_average(text: str) -> tuple[float, float, float] | None:
    match = re.search(r"load average:\s*([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)", text)
    if not match:
        return None
    return tuple(float(value) for value in match.groups())  # type: ignore[return-value]


def analyze_cpu(results: list[CommandResult]) -> tuple[list[EvidenceItem], list[str], list[str], str]:
    evidence: list[EvidenceItem] = []
    causes: list[str] = []
    suggestions: list[str] = []
    risk = "info"
    by_command = {result.command: result for result in results}

    uptime = by_command.get("uptime")
    if uptime and uptime.stdout:
        loads = _load_average(uptime.stdout)
        if loads:
            load1, load5, load15 = loads
            severity = "critical" if load1 >= 4 else "warning" if load1 >= 2 else "info"
            risk = severity if severity != "info" else risk
            evidence.append(EvidenceItem("uptime", "load_average", f"1m={load1}, 5m={load5}, 15m={load15}", severity))
            if severity != "info":
                causes.append("System load is elevated and should be correlated with top CPU processes.")

    ps_result = by_command.get("ps aux --sort=-%cpu | head")
    if ps_result and ps_result.stdout:
        lines = [line for line in ps_result.stdout.splitlines() if line.strip()]
        if len(lines) > 1:
            top_process = lines[1]
            evidence.append(EvidenceItem("ps", "top_cpu_process", top_process, "warning"))
            causes.append("A small set of processes appears to dominate CPU usage.")
            suggestions.append("Check whether the top process is expected workload, a runaway job, or needs rate limiting.")

    top_result = by_command.get("top -b -n 1 | head -30")
    if top_result and top_result.stdout:
        cpu_line = next((line for line in top_result.stdout.splitlines() if "%Cpu" in line), "")
        if cpu_line:
            evidence.append(EvidenceItem("top", "cpu_snapshot", cpu_line, "info"))

    if not suggestions:
        suggestions.append("Capture repeated samples to distinguish a spike from sustained CPU pressure.")
    if not causes:
        causes.append("No CPU pressure pattern was identified from the collected read-only evidence.")
    return evidence, causes, suggestions, risk
