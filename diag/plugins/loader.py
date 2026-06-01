from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

from diag.hooks.hook_manager import HookManager
from diag.plugins.manifest import PluginManifest
from diag.plugins.plugin_context import PluginContext
from diag.plugins.registry import PluginRecord, PluginRegistry
from diag.plugins.sandbox import sandbox_allows
from diag.plugins.validator import validate_manifest
from diag.tools.registry import ToolRegistry, build_default_registry
from diag.utils.config_loader import load_config
from diag.utils.paths import project_root


def plugins_root() -> Path:
    return project_root() / "plugins"


def plugins_config_path() -> Path:
    return project_root() / "configs" / "plugins.yaml"


def enabled_plugins() -> list[str]:
    config = load_config()
    enabled = config.get("plugins", {}).get("enabled", [])
    return list(enabled) if isinstance(enabled, list) else []


def write_enabled_plugins(names: list[str]) -> None:
    unique = sorted(set(names))
    plugins_config_path().write_text("plugins:\n  enabled: [" + ", ".join(unique) + "]\n", encoding="utf-8")


class PluginLoader:
    def discover(self) -> PluginRegistry:
        registry = PluginRegistry()
        enabled = set(enabled_plugins())
        root = plugins_root()
        if not root.exists():
            return registry
        for manifest_path in sorted(root.glob("*/plugin.yaml")):
            manifest = PluginManifest.from_file(manifest_path)
            errors = validate_manifest(manifest)
            ok, sandbox_message = sandbox_allows(manifest)
            if not ok:
                errors.append(sandbox_message)
            registry.add(PluginRecord(manifest=manifest, enabled=manifest.name in enabled, valid=not errors, errors=errors))
        return registry

    def _import_entry(self, manifest: PluginManifest) -> ModuleType:
        if not manifest.path:
            raise FileNotFoundError("manifest path missing")
        entry_path = manifest.path / manifest.entry
        spec = importlib.util.spec_from_file_location(f"opspilot_plugin_{manifest.name}", entry_path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot import plugin entry {entry_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_enabled(self, tool_registry: ToolRegistry, hook_manager: HookManager | None = None) -> list[PluginRecord]:
        loaded: list[PluginRecord] = []
        for record in self.discover().list():
            if not record.enabled or not record.valid:
                continue
            try:
                module = self._import_entry(record.manifest)
                register = getattr(module, "register", None)
                context = PluginContext(tool_registry, hook_manager)
                if callable(register):
                    register(context)
                loaded.append(PluginRecord(record.manifest, record.enabled, True, [], dict(context.analyzers)))
            except Exception as exc:
                loaded.append(PluginRecord(record.manifest, record.enabled, False, [f"load failed: {exc}"]))
        return loaded

    def enable(self, name: str) -> None:
        names = enabled_plugins()
        if name not in names:
            names.append(name)
        write_enabled_plugins(names)

    def disable(self, name: str) -> None:
        write_enabled_plugins([item for item in enabled_plugins() if item != name])

    def doctor(self, name: str) -> PluginRecord | None:
        record = self.discover().get(name)
        if not record or not record.valid:
            return record
        try:
            module = self._import_entry(record.manifest)
            register = getattr(module, "register", None)
            context = PluginContext(build_default_registry(), HookManager())
            if callable(register):
                register(context)
        except Exception as exc:
            return PluginRecord(record.manifest, record.enabled, False, [f"doctor failed: {exc}"])
        return PluginRecord(record.manifest, record.enabled, True, [], dict(context.analyzers))
