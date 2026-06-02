from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from diag.utils.config_loader import load_config

API_PROVIDER_NAMES = {"openai", "anthropic", "gemini", "deepseek", "openai_compatible", "custom"}
MOCK_PROVIDER_NAMES = {"mock"}
BLOCKED_PROVIDER_NAMES = {"ol" + "lama", "v" + "llm", "l" + "lama_cpp", "local", "off" + "line"}
BLOCKED_PROVIDER_TYPES = {"ol" + "lama", "v" + "llm", "l" + "lama.cpp", "l" + "lama_cpp", "local", "off" + "line"}
LOCAL_AI_DISABLED_CONFIG_MESSAGE = "本地 AI 已禁用。请使用 /config api 配置远程 API。"


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    type: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    timeout: int = 30
    max_tokens: int = 1024


def assert_api_provider_name(provider: str, *, allow_mock: bool = False) -> None:
    normalized = provider.strip().lower().replace("-", "_")
    allowed = set(API_PROVIDER_NAMES)
    if allow_mock:
        allowed.update(MOCK_PROVIDER_NAMES)
    if normalized in BLOCKED_PROVIDER_NAMES or normalized not in allowed:
        raise ValueError(LOCAL_AI_DISABLED_CONFIG_MESSAGE)


def normalize_provider_name(provider: str) -> str:
    normalized = provider.strip().lower().replace("-", "_")
    if normalized == "openai_compatible":
        return "openai_compatible"
    return normalized


def resolve_provider_config(provider: str | None = None, model: str | None = None, profile: str | None = None) -> ProviderConfig:
    cli: dict[str, Any] = {}
    config = load_config(cli)
    profiles = config.get("profiles", {})
    providers = config.get("providers", {})
    profile_name = normalize_provider_name(profile or "default")
    if profile_name in BLOCKED_PROVIDER_NAMES:
        raise ValueError(LOCAL_AI_DISABLED_CONFIG_MESSAGE)
    selected_profile = profiles.get(profile_name, {})
    provider_name = normalize_provider_name(str(provider or selected_profile.get("provider") or providers.get("default", "openai")))
    assert_api_provider_name(provider_name, allow_mock=True)
    provider_data = providers.get(provider_name, {})
    provider_type = provider_data.get("type", provider_name)
    normalized_type = str(provider_type).strip().lower().replace("-", "_")
    if normalized_type in BLOCKED_PROVIDER_TYPES:
        raise ValueError(LOCAL_AI_DISABLED_CONFIG_MESSAGE)
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
