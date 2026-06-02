from __future__ import annotations

import json
from typing import Any

from diag.ai.config import BLOCKED_PROVIDER_TYPES, ProviderConfig, resolve_provider_config
from diag.ai.errors import LLMConfigurationError, NeedApiConfig
from diag.ai.message import LLMMessage
from diag.ai.provider import LLMProvider
from diag.ai.providers.anthropic_provider import AnthropicProvider
from diag.ai.providers.mock_provider import MockProvider
from diag.ai.providers.openai_compatible_provider import OpenAICompatibleProvider
from diag.ai.providers.openai_provider import OpenAIProvider


def build_provider(config: ProviderConfig) -> LLMProvider:
    normalized_type = config.type.strip().lower().replace("-", "_")
    if normalized_type in BLOCKED_PROVIDER_TYPES:
        raise LLMConfigurationError("本地 AI 已禁用。请使用远程 API 地址。")
    if config.type == "mock":
        return MockProvider(config.model)
    if config.type == "openai":
        return OpenAIProvider(config.model, config.api_key_env or "OPENAI_API_KEY", config.base_url or "https://api.openai.com/v1", config.timeout, config.max_tokens)
    if config.type == "anthropic":
        return AnthropicProvider(config.model, config.api_key_env or "ANTHROPIC_API_KEY", config.base_url or "https://api.anthropic.com", config.timeout, config.max_tokens)
    return OpenAICompatibleProvider(config.base_url or "", config.api_key_env, config.model, config.name, config.timeout, config.max_tokens)


class ModelRouter:
    def __init__(self, provider: str | None = None, model: str | None = None, profile: str | None = None, force_mock: bool = False) -> None:
        config = resolve_provider_config(provider=provider, model=model, profile=profile)
        if force_mock:
            config = ProviderConfig(name="mock", type="mock", model="mock-diagnosis-v1")
        self.config = config
        try:
            self.provider = build_provider(config)
        except LLMConfigurationError as exc:
            if force_mock:
                raise
            raise NeedApiConfig(f"{exc} 请运行 /config api 配置远程 API。") from exc
        if not force_mock:
            if config.type == "mock":
                raise NeedApiConfig("正常模式必须配置远程 API；mock 仅用于 demo/test。")
            health = self.provider.healthcheck()
            if not health.ok:
                raise NeedApiConfig(f"{health.message}。请运行 /config api 并设置环境变量。")

    def planner(self, user_input: str, available_tools: list[str]) -> dict[str, Any]:
        prompt = (
            "Role: planner. Return only structured task and tool_calls. "
            "Never execute shell. Available tools: "
            + ", ".join(available_tools)
            + f"\nUser input: {user_input}"
        )
        response = self.provider.complete([LLMMessage("user", prompt)])
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError:
            data = {"task": None, "tool_calls": []}
        return {"provider": response.provider, "model": response.model, "result": data}

    def summarizer(self, evidence: list[dict[str, Any]]) -> str:
        response = self.provider.complete([LLMMessage("user", f"Role: summarizer. Summarize evidence without changing facts: {evidence}")])
        return response.content

    def risk_reviewer(self, command: str, risk_level: str) -> str:
        response = self.provider.complete(
            [LLMMessage("user", f"Role: risk_reviewer. Explain risk only; never override safety checker. Command={command} Risk={risk_level}")]
        )
        return response.content

    def report_writer(self, report_text: str) -> str:
        response = self.provider.complete([LLMMessage("user", f"Role: report_writer. Polish wording but preserve evidence facts:\n{report_text}")])
        return response.content
