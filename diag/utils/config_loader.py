from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from diag.utils.paths import project_root


DEFAULT_CONFIG: dict[str, Any] = {
    "providers": {"default": "mock", "mock": {"type": "mock", "model": "mock-diagnosis-v1"}},
    "profiles": {"default": {"provider": "mock", "model": "mock-diagnosis-v1"}},
    "plugins": {"enabled": []},
}


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            node: dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            parent[key] = _parse_scalar(value)
    return root


def read_config_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return parse_simple_yaml(text)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_config(cli_overrides: dict[str, Any] | None = None, home: Path | None = None) -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    home_config = home or (Path.home() / ".opspilot" / "config.yaml")
    config = deep_merge(config, read_config_file(home_config))

    configs_dir = project_root() / "configs"
    for path in sorted(configs_dir.glob("*.yaml")):
        if path.name == "local.yaml":
            continue
        config = deep_merge(config, read_config_file(path))
    local_config = configs_dir / "local.yaml"
    config = deep_merge(config, read_config_file(local_config))
    if cli_overrides:
        config = deep_merge(config, cli_overrides)
    return config
