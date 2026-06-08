from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentScope:
    name: str
    prompt_name: str
    tool_scenes: tuple[str, ...]


class BaseSubagent:
    scope = AgentScope("BaseAgent", "subagent_base", ())

    def __init__(self, sandbox_profile: str = "safe-read") -> None:
        self.sandbox_profile = sandbox_profile

    def label(self, activity: str) -> str:
        return f"[{self.scope.name}] {activity}"

    def tool_scenes(self) -> tuple[str, ...]:
        return self.scope.tool_scenes
