from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from diag.hooks.hook_manager import HookManager
from diag.plugins.validator import validate_tool_spec
from diag.tools.registry import ToolRegistry
from diag.tools.spec import ToolSpec


@dataclass
class PluginContext:
    registry: ToolRegistry
    hook_manager: HookManager | None = None
    analyzers: dict[str, Callable[..., Any]] = field(default_factory=dict)
    runbooks: dict[str, list[str]] = field(default_factory=dict)

    def register_tool(self, spec: ToolSpec) -> None:
        validate_tool_spec(spec)
        self.registry.register(spec)

    def register_hook(self, event: str, hook: Callable[..., Any]) -> None:
        if not self.hook_manager:
            return
        self.hook_manager.register(event, hook)

    def register_analyzer(self, name: str, analyzer: Callable[..., Any]) -> None:
        self.analyzers[name] = analyzer

    def register_runbook(self, name: str, tool_names: list[str]) -> None:
        self.runbooks[name] = tool_names
