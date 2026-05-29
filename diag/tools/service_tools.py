from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_service_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            "service.status",
            "Check service status",
            "systemctl status {service}",
            RiskLevel.SAFE_READONLY,
            ("service", "service-failed"),
        )
    )
    registry.register(
        ToolSpec(
            "service.logs",
            "Read recent service logs",
            "journalctl -u {service} -n 50",
            RiskLevel.SAFE_READONLY,
            ("service", "service-failed"),
        )
    )
    registry.register(ToolSpec("service.ports", "Check listening ports", "ss -tulnp", RiskLevel.SAFE_READONLY, ("service", "service-failed")))
