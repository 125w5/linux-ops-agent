from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from diag.utils.config_loader import load_config


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    type: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    timeout: int = 30
    max_tokens: int = 1024


def resolve_provider_config(provider: str | None = None, model: str | None = None, profile: str | None = None) -> ProviderConfig:
    cli: dict[str, Any] = {}
    config = load_config(cli)
    profiles = config.get("profiles", {})
    providers = config.get("providers", {})
    selected_profile = profiles.get(profile or "default", {})
    provider_name = provider or selected_profile.get("provider") or providers.get("default", "mock")
    provider_data = providers.get(provider_name, {})
    provider_type = provider_data.get("type", provider_name)
    selected_model = model or (provider_data.get("model") if provider else selected_profile.get("model")) or provider_data.get("model", "mock-diagnosis-v1")
    return ProviderConfig(
        name=provider_name,
        type=provider_type,
        model=selected_model,
        base_url=provider_data.get("base_url"),
        api_key_env=provider_data.get("api_key_env"),
        timeout=int(provider_data.get("timeout", 30)),
        max_tokens=int(provider_data.get("max_tokens", 1024)),
    )
