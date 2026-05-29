from __future__ import annotations

from diag.core.models import CommandResult, EvidenceItem


def analyze_service(results: list[CommandResult], service: str = "nginx") -> tuple[list[EvidenceItem], list[str], list[str], str]:
    evidence: list[EvidenceItem] = []
    causes: list[str] = []
    suggestions: list[str] = []
    risk = "info"
    by_command = {result.command: result for result in results}
    status_cmd = f"systemctl status {service}"
    logs_cmd = f"journalctl -u {service} -n 50"

    status = by_command.get(status_cmd)
    if status and status.stdout:
        lower = status.stdout.lower()
        if "active: failed" in lower or "failed" in lower:
            risk = "critical"
            evidence.append(EvidenceItem("systemctl", "service_state", f"{service} is failed", "critical"))
            causes.append(f"{service} is not running successfully.")

    logs = by_command.get(logs_cmd)
    if logs and logs.stdout:
        lower = logs.stdout.lower()
        if "address already in use" in lower or "bind()" in lower:
            risk = "critical"
            evidence.append(EvidenceItem("journalctl", "port_conflict", "Service log reports address already in use.", "critical"))
            causes.append("A port conflict is likely preventing the service from starting.")
            suggestions.append("Identify the process holding the target port before changing service configuration.")
        if "configuration file" in lower and "failed" in lower:
            evidence.append(EvidenceItem("journalctl", "config_error", "Service log reports configuration test failure.", "warning"))
            causes.append("Configuration validation failed during service startup.")
            suggestions.append("Run the service configuration test command and inspect the referenced file.")
        if "permission denied" in lower:
            evidence.append(EvidenceItem("journalctl", "permission_error", "Service log contains permission denied.", "warning"))
            causes.append("A filesystem or runtime permission problem may be blocking startup.")

    ports = by_command.get("ss -tulnp")
    if ports and ports.stdout:
        matching = [line for line in ports.stdout.splitlines() if ":80" in line]
        if matching:
            evidence.append(EvidenceItem("ss", "listening_ports", "; ".join(matching), "warning"))

    if not suggestions:
        suggestions.append("Review service status, recent logs, and listening ports before restarting anything.")
    if not causes:
        causes.append("No obvious service failure pattern was identified from read-only evidence.")
    return evidence, causes, suggestions, risk
