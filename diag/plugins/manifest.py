from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from diag.utils.config_loader import read_config_file


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    entry: str
    permissions: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    demo_fixtures: list[str] = field(default_factory=list)
    ui: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    @classmethod
    def from_file(cls, path: Path) -> "PluginManifest":
        data: dict[str, Any] = read_config_file(path)
        return cls(
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            description=str(data.get("description", "")),
            entry=str(data.get("entry", "")),
            permissions=list(data.get("permissions", [])),
            exports=list(data.get("exports", [])),
            demo_fixtures=list(data.get("demo_fixtures", [])),
            ui=dict(data.get("ui", {})) if isinstance(data.get("ui", {}), dict) else {},
            path=path.parent,
        )
