from __future__ import annotations

import urllib.error
import urllib.request

from diag.ai.config import resolve_provider_config
from diag.ai.model_router import build_provider
from diag.utils.config_loader import load_config


def list_models() -> str:
    providers = load_config().get("providers", {})
    lines = []
    for name, data in providers.items():
        if name == "default" or not isinstance(data, dict):
            continue
        lines.append(f"{name}: type={data.get('type', name)} model={data.get('model', '(default)')}")
    return "\n".join(lines)


def doctor_provider(name: str | None = None) -> str:
    names = [name] if name else ["mock", "openai", "anthropic", "ollama"]
    lines = []
    for provider_name in names:
        try:
            config = resolve_provider_config(provider=provider_name)
            provider = build_provider(config)
            health = provider.healthcheck()
            if provider_name == "ollama" and health.ok:
                base = (config.base_url or "http://localhost:11434").rstrip("/")
                try:
                    urllib.request.urlopen(f"{base}/api/tags", timeout=1).close()
                except (urllib.error.URLError, TimeoutError, OSError):
                    health = type(health)(False, health.provider, "ollama unreachable")
            status = "ok" if health.ok else "missing env" if "Missing API key env var" in health.message else "unreachable"
            lines.append(f"{provider_name}: {status} model={config.model} note={health.message}")
        except Exception as exc:
            message = str(exc)
            if "API" in message and "=" in message:
                message = "configuration error"
            lines.append(f"{provider_name}: unreachable note={message}")
    lines.append("demo: force_mock enabled so demo never calls cloud providers")
    return "\n".join(lines)
