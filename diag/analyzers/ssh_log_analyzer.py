from __future__ import annotations

import re
from collections import Counter

from diag.core.models import CommandResult, EvidenceItem


IP_RE = re.compile(r"from\s+([0-9a-fA-F:.]+)")
FAILED_USER_RE = re.compile(r"Failed password for (?:invalid user )?(\S+) from")
INVALID_USER_RE = re.compile(r"Invalid user (\S+) from")


def analyze_ssh_failures(results: list[CommandResult]) -> tuple[list[EvidenceItem], list[str], list[str], str]:
    evidence: list[EvidenceItem] = []
    causes: list[str] = []
    suggestions: list[str] = []
    failed_lines: list[str] = []
    invalid_lines: list[str] = []

    for result in results:
        if "Failed password" in result.command and result.stdout:
            failed_lines.extend([line for line in result.stdout.splitlines() if "Failed password" in line])
        if "Invalid user" in result.command and result.stdout:
            invalid_lines.extend([line for line in result.stdout.splitlines() if "Invalid user" in line])

    ip_counter = Counter()
    user_counter = Counter()
    for line in failed_lines + invalid_lines:
        ip_match = IP_RE.search(line)
        if ip_match:
            ip_counter[ip_match.group(1)] += 1
        user_match = FAILED_USER_RE.search(line) or INVALID_USER_RE.search(line)
        if user_match:
            user_counter[user_match.group(1)] += 1

    failed_count = len(failed_lines)
    invalid_count = len(invalid_lines)
    risk = "critical" if failed_count >= 20 or (ip_counter and ip_counter.most_common(1)[0][1] >= 10) else "warning" if failed_count >= 5 else "info"

    evidence.append(EvidenceItem("auth.log", "failed_password_count", str(failed_count), risk))
    evidence.append(EvidenceItem("auth.log", "invalid_user_count", str(invalid_count), "warning" if invalid_count else "info"))
    if ip_counter:
        evidence.append(EvidenceItem("auth.log", "source_ips", ", ".join(f"{ip}={count}" for ip, count in ip_counter.most_common()), risk))
        causes.append("Repeated SSH authentication failures from one or more source IPs indicate possible brute-force activity.")
    if user_counter:
        evidence.append(EvidenceItem("auth.log", "usernames", ", ".join(f"{user}={count}" for user, count in user_counter.most_common()), "info"))

    suggestions.extend(
        [
            "Review whether source IPs are expected administrative hosts.",
            "Prefer key-based login and disable password login where policy allows.",
            "Consider rate limiting or fail2ban-style controls after review.",
        ]
    )
    if not causes:
        causes.append("No SSH brute-force pattern was identified from the collected log sample.")
    return evidence, causes, suggestions, risk
