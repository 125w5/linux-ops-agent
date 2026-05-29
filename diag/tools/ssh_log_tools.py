from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_ssh_log_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            "ssh.failed_passwords",
            "Collect failed SSH login records",
            "grep 'Failed password' /var/log/auth.log | tail -100",
            RiskLevel.SAFE_READONLY,
            ("ssh-failure", "ssh"),
        )
    )
    registry.register(
        ToolSpec(
            "ssh.invalid_users",
            "Collect invalid SSH user records",
            "grep 'Invalid user' /var/log/auth.log | tail -100",
            RiskLevel.SAFE_READONLY,
            ("ssh-failure", "ssh"),
        )
    )
    registry.register(
        ToolSpec(
            "ssh.failed_ip_count",
            "Count failed login sources",
            "grep 'Failed password' /var/log/auth.log | awk '{{print $(NF-3)}}' | sort | uniq -c | sort -nr | head",
            RiskLevel.SAFE_READONLY,
            ("ssh-failure", "ssh"),
        )
    )
