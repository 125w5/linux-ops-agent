from __future__ import annotations

import re

from diag.core.models import CommandResult, EvidenceItem


def _parse_percent(value: str) -> int | None:
    match = re.search(r"(\d+)%", value)
    return int(match.group(1)) if match else None


def analyze_disk(results: list[CommandResult]) -> tuple[list[EvidenceItem], list[str], list[str], str]:
    evidence: list[EvidenceItem] = []
    root_causes: list[str] = []
    suggestions: list[str] = []
    risk_level = "info"

    by_command = {result.command: result for result in results}
    df_result = by_command.get("df -h")
    if df_result and df_result.stdout:
        for line in df_result.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 6:
                usage = _parse_percent(parts[4])
                mount = parts[-1]
                if usage is not None and usage >= 95:
                    risk_level = "critical"
                    evidence.append(EvidenceItem("df -h", "filesystem_usage", f"{mount} usage is {usage}%", "critical"))
                elif usage is not None and usage >= 85:
                    if risk_level != "critical":
                        risk_level = "warning"
                    evidence.append(EvidenceItem("df -h", "filesystem_usage", f"{mount} usage is {usage}%", "warning"))

    du_result = by_command.get("du -h --max-depth=1 / 2>/dev/null | sort -hr | head")
    if du_result and du_result.stdout:
        top_lines = [line for line in du_result.stdout.splitlines() if line.strip()][:5]
        if top_lines:
            evidence.append(EvidenceItem("du", "large_directories", "; ".join(top_lines), "info"))
            joined = "\n".join(top_lines)
            if "/var/log" in joined:
                root_causes.append("Log files under /var/log are a likely contributor.")
                suggestions.append("Review logrotate policy and archive or compress old logs.")
            if "/var/lib/docker" in joined:
                root_causes.append("Docker images, layers, volumes, or build cache may be consuming space.")
                suggestions.append("Review Docker usage before cleaning unused images, containers, volumes, or build cache.")

    large_files = by_command.get("find / -type f -size +500M 2>/dev/null | head")
    if large_files and large_files.stdout:
        files = [line.strip() for line in large_files.stdout.splitlines() if line.strip()]
        evidence.append(EvidenceItem("find", "large_files", "; ".join(files[:5]), "warning" if files else "info"))
        if files:
            root_causes.append("One or more files larger than 500 MB were found.")
            suggestions.append("Confirm file ownership and retention needs before removing or truncating large files.")

    journal = by_command.get("journalctl --disk-usage")
    if journal and journal.stdout:
        evidence.append(EvidenceItem("journalctl", "journal_usage", journal.stdout.strip(), "info"))
        if re.search(r"(\d+(?:\.\d+)?)G", journal.stdout):
            suggestions.append("Consider a safe journal retention policy after approval, for example vacuum by time or size.")

    docker = by_command.get("docker system df")
    if docker and docker.stdout:
        evidence.append(EvidenceItem("docker", "docker_usage", "Docker disk usage was collected.", "info"))

    if not root_causes:
        root_causes.append("No single dominant cause was identified from the collected read-only evidence.")
    if not suggestions:
        suggestions.append("Collect a deeper directory breakdown for the busiest mount point before taking action.")

    return evidence, root_causes, suggestions, risk_level
