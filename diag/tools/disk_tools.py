from __future__ import annotations

from diag.core.models import RiskLevel
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


def register_disk_tools(registry: ToolRegistry) -> None:
    registry.register(ToolSpec("disk.df", "Check filesystem usage", "df -h", RiskLevel.SAFE_READONLY, ("disk",)))
    registry.register(
        ToolSpec(
            "disk.root_dirs",
            "Locate large top-level directories",
            "du -h --max-depth=1 / 2>/dev/null | sort -hr | head",
            RiskLevel.SAFE_READONLY,
            ("disk",),
        )
    )
    registry.register(
        ToolSpec(
            "disk.large_files",
            "Find large files",
            "find / -type f -size +500M 2>/dev/null | head",
            RiskLevel.SAFE_READONLY,
            ("disk",),
        )
    )
    registry.register(
        ToolSpec("disk.journal_usage", "Check journal disk usage", "journalctl --disk-usage", RiskLevel.SAFE_READONLY, ("disk",))
    )
    registry.register(ToolSpec("disk.docker_usage", "Check Docker disk usage", "docker system df", RiskLevel.SAFE_READONLY, ("disk",)))
