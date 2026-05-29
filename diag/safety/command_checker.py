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

DANGEROUS_PATTERNS = (
    "rm ",
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
    "kill ",
    "userdel",
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


def check_command(command: str) -> SafetyDecision:
    normalized = f" {command.strip().lower()} "
    for pattern in DANGEROUS_PATTERNS:
        if pattern in normalized:
            return SafetyDecision(False, RiskLevel.BLOCKED, f"Blocked dangerous pattern: {pattern.strip()}")

    first_tokens = [_first_token(segment) for segment in _segments(command)]
    if first_tokens and all(token in READONLY_ALLOW for token in first_tokens):
        return SafetyDecision(True, RiskLevel.SAFE_READONLY, "Read-only command chain")

    return SafetyDecision(False, RiskLevel.HIGH_RISK, "Command is not in read-only allow list")
