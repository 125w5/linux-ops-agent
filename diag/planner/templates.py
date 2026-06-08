from __future__ import annotations

from diag.core.models import DiagnosisStep
from diag.tools.registry import ToolRegistry, build_default_registry
from diag.tools.spec import step_id_from_tool


RUNBOOKS: dict[str, list[DiagnosisStep]] = {
    "disk": [
        DiagnosisStep("check_df", "Check filesystem usage", "df -h"),
        DiagnosisStep(
            "check_root_dirs",
            "Locate large top-level directories",
            "du -h --max-depth=1 / 2>/dev/null | sort -hr | head",
        ),
        DiagnosisStep(
            "check_large_files",
            "Find large files",
            "find / -type f -size +500M 2>/dev/null | head",
        ),
        DiagnosisStep(
            "check_journal",
            "Check journal disk usage",
            "journalctl --disk-usage",
            required=False,
        ),
        DiagnosisStep(
            "check_docker",
            "Check Docker disk usage",
            "docker system df",
            required=False,
        ),
    ],
    "cpu": [
        DiagnosisStep("check_uptime", "Check load average", "uptime"),
        DiagnosisStep("check_top", "Capture top snapshot", "top -b -n 1 | head -30"),
        DiagnosisStep("check_cpu_processes", "List high CPU processes", "ps aux --sort=-%cpu | head"),
    ],
    "service": [
        DiagnosisStep("check_service", "Check nginx service status", "systemctl status nginx"),
        DiagnosisStep("check_service_logs", "Read recent nginx logs", "journalctl -u nginx -n 50"),
        DiagnosisStep("check_ports", "Check listening ports", "ss -tulnp"),
    ],
    "ssh-failure": [
        DiagnosisStep(
            "check_failed_password",
            "Collect failed SSH login records",
            "grep 'Failed password' /var/log/auth.log | tail -100",
        ),
        DiagnosisStep(
            "count_failed_ip",
            "Count failed login sources",
            "grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head",
        ),
    ],
}

RUNBOOKS["ssh"] = RUNBOOKS["ssh-failure"]


def get_runbook(task_type: str, registry: ToolRegistry | None = None, service: str = "nginx") -> list[DiagnosisStep]:
    registry = registry or build_default_registry()
    specs = registry.for_scene(task_type)
    if not specs:
        try:
            return RUNBOOKS[task_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported task: {task_type}") from exc

    args = {"service": service}
    return [
        DiagnosisStep(
            id=step_id_from_tool(spec.name),
            name=spec.description,
            command=spec.render(args),
            risk=spec.risk,
            required=True,
            tool_name=spec.name,
            tool_args=args if "{service}" in spec.command_template else {},
        )
        for spec in specs
    ]
