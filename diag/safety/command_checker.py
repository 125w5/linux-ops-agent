from __future__ import annotations

import shlex
from dataclasses import dataclass

from diag.core.models import RiskLevel


READONLY_ALLOW = {
    "awk",
    "cat",
    "df",
    "du",
    "find",
    "free",
    "grep",
    "head",
    "journalctl",
    "man",
    "ps",
    "pstree",
    "sort",
    "ss",
    "systemctl",
    "tail",
    "top",
    "uniq",
    "uptime",
    "vmstat",
    "docker",
}

LOW_RISK_ALLOW = {
    "nginx -t",
    "systemctl cat",
}

DANGEROUS_PATTERNS = (
    "rm -",
    "mkfs",
    " dd ",
    "chmod",
    "chown",
    "reboot",
    "shutdown",
    "poweroff",
    "halt",
    "init ",
    "systemctl restart",
    "systemctl stop",
    "systemctl start",
    "docker system prune",
    "journalctl --vacuum",
    "userdel",
)

BLOCKED_KILL_PATTERNS = (
    "kill -9",
    "kill -kill",
    "kill -sigkill",
)


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    risk_level: RiskLevel
    reason: str


def _segments(command: str) -> list[str]:
    return [part.strip() for part in command.split("|") if part.strip()]


def _first_token(segment: str) -> str:
    cleaned = segment.split("2>/dev/null", 1)[0].strip()
    try:
        tokens = shlex.split(cleaned)
    except ValueError:
        tokens = cleaned.split()
    if not tokens:
        return ""
    return tokens[0]


def _is_low_risk_command(command: str) -> bool:
    segments = _segments(command)
    if len(segments) != 1:
        return False
    normalized = segments[0].strip().lower()
    return any(normalized == pattern or normalized.startswith(pattern + " ") for pattern in LOW_RISK_ALLOW)


def check_command(command: str) -> SafetyDecision:
    normalized = f" {command.strip().lower()} "
    if any(token == "rm" for token in (_first_token(segment) for segment in _segments(command))):
        return SafetyDecision(False, RiskLevel.BLOCKED, "Blocked dangerous command: rm")
    for pattern in DANGEROUS_PATTERNS:
        if pattern in normalized:
            return SafetyDecision(False, RiskLevel.BLOCKED, f"Blocked dangerous pattern: {pattern.strip()}")
    for pattern in BLOCKED_KILL_PATTERNS:
        if pattern in normalized:
            return SafetyDecision(False, RiskLevel.BLOCKED, "Blocked SIGKILL command")

    if _is_low_risk_command(command):
        return SafetyDecision(True, RiskLevel.LOW_RISK, "Low-risk validation/read command")
    if normalized.startswith(" kill -15 ") or normalized.startswith(" kill -term "):
        return SafetyDecision(True, RiskLevel.LOW_RISK, "Process termination requires confirmation")

    first_tokens = [_first_token(segment) for segment in _segments(command)]
    if first_tokens and all(token in READONLY_ALLOW for token in first_tokens):
        return SafetyDecision(True, RiskLevel.SAFE_READONLY, "Read-only command chain")

    return SafetyDecision(False, RiskLevel.HIGH_RISK, "Command is not in read-only allow list")
