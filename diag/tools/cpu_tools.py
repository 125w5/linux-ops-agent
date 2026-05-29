from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_cpu_tools(registry: ToolRegistry) -> None:
    registry.register(ToolSpec("cpu.uptime", "Check load average", "uptime", RiskLevel.SAFE_READONLY, ("cpu",)))
    registry.register(ToolSpec("cpu.top", "Capture top snapshot", "top -b -n 1 | head -30", RiskLevel.SAFE_READONLY, ("cpu",)))
    registry.register(ToolSpec("cpu.ps", "List high CPU processes", "ps aux --sort=-%cpu | head", RiskLevel.SAFE_READONLY, ("cpu",)))
