from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from diag.utils.config_loader import load_config
from diag.utils.paths import project_root


CONFIG_TABS = ["General", "Models", "Providers", "Plugins", "Permissions", "Resources", "UI", "Keybindings"]


@dataclass(frozen=True)
class ConfigDiff:
    path: Path
    before: str
    after: str

    def render(self) -> str:
        return f"--- before: {self.path}\n{self.before}\n--- after: {self.path}\n{self.after}"


def config_sources() -> list[str]:
    return ["defaults", "user", "configs", "configs/local.yaml", "CLI"]


def redact_provider_env_status() -> dict[str, str]:
    providers = load_config().get("providers", {})
    status: dict[str, str] = {}
    for name, data in providers.items():
        if name == "default" or not isinstance(data, dict):
            continue
        env_name = data.get("api_key_env")
        if env_name:
            status[name] = f"{env_name}={'set' if os.environ.get(str(env_name)) else 'missing'}"
        else:
            status[name] = "no api key env required"
    return status


def preview_local_yaml_update(section: str, key: str, value: str) -> ConfigDiff:
    path = project_root() / "configs" / "local.yaml"
    before = path.read_text(encoding="utf-8") if path.exists() else ""
    after = before.rstrip() + f"\n{section}:\n  {key}: {value}\n"
    return ConfigDiff(path, before, after)


def save_local_yaml(diff: ConfigDiff) -> None:
    diff.path.parent.mkdir(parents=True, exist_ok=True)
    diff.path.write_text(diff.after, encoding="utf-8")


def save_config_value(section: str, key: str, value: str) -> ConfigDiff:
    diff = preview_local_yaml_update(section, key, value)
    save_local_yaml(diff)
    return diff


def render_config_screen() -> str:
    lines = ["Config", "Tabs: " + ", ".join(CONFIG_TABS), "Sources: " + " -> ".join(config_sources()), "Provider env:"]
    lines.extend(f"- {name}: {status}" for name, status in redact_provider_env_status().items())
    return "\n".join(lines)
