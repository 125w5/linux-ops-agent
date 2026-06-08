from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_ops_tools(registry: ToolRegistry) -> None:
    registry.register(ToolSpec("nginx.config_test", "Validate nginx configuration", "nginx -t", RiskLevel.LOW_RISK, ("service", "nginx")))
    registry.register(ToolSpec("docker.ps", "List Docker containers", "docker ps", RiskLevel.SAFE_READONLY, ("docker", "service", "disk")))
    registry.register(ToolSpec("docker.logs", "Read recent Docker logs", "docker logs --tail 100 {service}", RiskLevel.SAFE_READONLY, ("docker",)))
    registry.register(ToolSpec("systemd.failed_units", "List failed systemd units", "systemctl --failed", RiskLevel.SAFE_READONLY, ("service", "systemd")))
    registry.register(ToolSpec("systemd.cat", "Read systemd unit file", "systemctl cat {service}", RiskLevel.LOW_RISK, ("service", "systemd")))
    registry.register(ToolSpec("network.listen", "List listening sockets", "ss -tulnp", RiskLevel.SAFE_READONLY, ("network", "service")))
    registry.register(ToolSpec("security.sudo_log", "Read sudo log entries", "grep sudo /var/log/auth.log | tail -100", RiskLevel.SAFE_READONLY, ("security", "ssh-failure")))
    registry.register(ToolSpec("mysql.status", "Check MySQL service status", "systemctl status mysql", RiskLevel.SAFE_READONLY, ("mysql", "service")))
