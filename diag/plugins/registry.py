from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any

from diag.plugins.manifest import PluginManifest


@dataclass(frozen=True)
class PluginRecord:
    manifest: PluginManifest
    enabled: bool
    valid: bool
    errors: list[str]
    analyzers: dict[str, Callable[..., Any]] | None = None


class PluginRegistry:
    def __init__(self) -> None:
        self.records: dict[str, PluginRecord] = {}

    def add(self, record: PluginRecord) -> None:
        self.records[record.manifest.name] = record

    def list(self) -> list[PluginRecord]:
        return list(self.records.values())

    def get(self, name: str) -> PluginRecord | None:
        return self.records.get(name)
