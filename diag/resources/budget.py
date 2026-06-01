from __future__ import annotations

from dataclasses import dataclass

from diag.utils.config_loader import load_config


@dataclass(frozen=True)
class AIBudget:
    max_calls_per_session: int = 4
    allow_cloud_in_demo: bool = False


@dataclass(frozen=True)
class ResourceBudget:
    command_timeout_seconds: int = 15
    max_commands_per_session: int = 20
    max_stdout_bytes_per_command: int = 65536
    max_total_output_bytes: int = 262144
    max_log_lines: int = 300
    max_report_bytes: int = 1048576
    ai: AIBudget = AIBudget()


def load_resource_budget() -> ResourceBudget:
    data = load_config().get("resources", {})
    ai = data.get("ai", {}) if isinstance(data.get("ai", {}), dict) else {}
    return ResourceBudget(
        command_timeout_seconds=int(data.get("command_timeout_seconds", 15)),
        max_commands_per_session=int(data.get("max_commands_per_session", 20)),
        max_stdout_bytes_per_command=int(data.get("max_stdout_bytes_per_command", 65536)),
        max_total_output_bytes=int(data.get("max_total_output_bytes", 262144)),
        max_log_lines=int(data.get("max_log_lines", 300)),
        max_report_bytes=int(data.get("max_report_bytes", 1048576)),
        ai=AIBudget(
            max_calls_per_session=int(ai.get("max_calls_per_session", 4)),
            allow_cloud_in_demo=bool(ai.get("allow_cloud_in_demo", False)),
        ),
    )
