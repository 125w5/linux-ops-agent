from __future__ import annotations

from dataclasses import dataclass, field

from diag.tools.spec import ToolSpec


@dataclass
class ToolRegistry:
    _tools: dict[str, ToolSpec] = field(default_factory=dict)

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Duplicate tool spec: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def list(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def for_scene(self, scene: str) -> list[ToolSpec]:
        return [spec for spec in self._tools.values() if scene in spec.scenes]


def build_default_registry() -> ToolRegistry:
    from diag.tools.cpu_tools import register_cpu_tools
    from diag.tools.disk_tools import register_disk_tools
    from diag.tools.ops_tools import register_ops_tools
    from diag.tools.process_tools import register_process_tools
    from diag.tools.service_tools import register_service_tools
    from diag.tools.ssh_log_tools import register_ssh_log_tools

    registry = ToolRegistry()
    register_disk_tools(registry)
    register_cpu_tools(registry)
    register_service_tools(registry)
    register_ssh_log_tools(registry)
    register_ops_tools(registry)
    register_process_tools(registry)
    return registry
