from __future__ import annotations

from dataclasses import dataclass, field

from diag.core.models import RiskLevel


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    command_template: str
    risk: RiskLevel
    scenes: tuple[str, ...]

    def render(self, args: dict[str, str] | None = None) -> str:
        return self.command_template.format(**(args or {}))


@dataclass(frozen=True)
class ToolCall:
    tool_name: str
    args: dict[str, str] = field(default_factory=dict)


def step_id_from_tool(name: str) -> str:
    return name.replace(".", "_").replace("-", "_")
