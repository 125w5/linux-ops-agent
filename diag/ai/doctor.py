from __future__ import annotations

from diag.ai.config import LOCAL_AI_DISABLED_CONFIG_MESSAGE, resolve_provider_config
from diag.ai.errors import LLMConfigurationError
from diag.ai.model_router import build_provider
from diag.ai.remote_url_validator import LOCAL_AI_DISABLED_MESSAGE
from diag.utils.config_loader import load_config


API_ONLY_PROVIDER_NAMES = ["mock", "openai", "anthropic", "gemini", "deepseek", "openai_compatible", "custom"]


def list_models() -> str:
    providers = load_config().get("providers", {})
    lines = []
    for name, data in providers.items():
        if name == "default" or not isinstance(data, dict):
            continue
        if name not in API_ONLY_PROVIDER_NAMES:
            continue
        lines.append(f"{name}: type={data.get('type', name)} model={data.get('model', '(default)')}")
    return "\n".join(lines)


def doctor_provider(name: str | None = None) -> str:
    names = [name] if name else API_ONLY_PROVIDER_NAMES
    lines = []
    for provider_name in names:
        try:
            config = resolve_provider_config(provider=provider_name)
            provider = build_provider(config)
            health = provider.healthcheck()
            status = "ok" if health.ok else "missing_env" if "Missing API key env var" in health.message else "unreachable"
            note = health.message
            if status == "missing_env":
                note = f"请设置环境变量，例如 {config.api_key_env}"
            lines.append(f"{provider_name}: {status} model={config.model} note={note}")
        except LLMConfigurationError as exc:
            status = "blocked_local_ai" if LOCAL_AI_DISABLED_MESSAGE in str(exc) else "config_error"
            note = "本地 AI 已禁用，请使用远程 API。" if status == "blocked_local_ai" else str(exc)
            lines.append(f"{provider_name}: {status} model=(unknown) note={note}")
        except ValueError as exc:
            status = "blocked_local_ai" if LOCAL_AI_DISABLED_CONFIG_MESSAGE in str(exc) else "config_error"
            note = "本地 AI 已禁用，请使用远程 API。" if status == "blocked_local_ai" else str(exc)
            lines.append(f"{provider_name}: {status} model=(unknown) note={note}")
        except Exception as exc:
            lines.append(f"{provider_name}: unreachable note={exc}")
    lines.append("demo: mock only; demo never calls remote APIs")
    return "\n".join(lines)
