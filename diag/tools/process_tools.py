from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_process_tools(registry: ToolRegistry) -> None:
    registry.register(ToolSpec("process.list_top_cpu", "List top CPU processes", "ps aux --sort=-%cpu | head", RiskLevel.SAFE_READONLY, ("process", "cpu")))
    registry.register(ToolSpec("process.list_top_memory", "List top memory processes", "ps aux --sort=-%mem | head", RiskLevel.SAFE_READONLY, ("process", "memory")))
    registry.register(ToolSpec("process.inspect", "Inspect one process", "ps -fp {pid}", RiskLevel.SAFE_READONLY, ("process",)))
    registry.register(ToolSpec("process.tree", "Show process tree", "pstree -ap {pid}", RiskLevel.SAFE_READONLY, ("process",)))
    registry.register(ToolSpec("process.kill_term", "Send SIGTERM after approval", "kill -TERM {pid}", RiskLevel.LOW_RISK, ("process",)))
    registry.register(ToolSpec("process.kill_kill", "SIGKILL is blocked by default", "kill -9 {pid}", RiskLevel.BLOCKED, ("process",)))
