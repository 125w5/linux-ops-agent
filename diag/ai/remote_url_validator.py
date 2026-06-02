from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from diag.ai.errors import LLMConfigurationError


LOCAL_AI_DISABLED_MESSAGE = "本地 AI 已禁用。请使用远程 API 地址。"


def validate_remote_api_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme in {"file", "http+unix", "unix"}:
        raise LLMConfigurationError(LOCAL_AI_DISABLED_MESSAGE)
    if parsed.scheme not in {"http", "https"}:
        raise LLMConfigurationError("请使用 http 或 https 远程 API 地址。")
    host = parsed.hostname
    if not host:
        raise LLMConfigurationError("请填写远程 API base_url。")
    lowered = host.lower()
    if lowered in {"localhost", "0.0.0.0"}:
        raise LLMConfigurationError(LOCAL_AI_DISABLED_MESSAGE)
    try:
        ip = ipaddress.ip_address(lowered)
    except ValueError:
        return base_url
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_unspecified:
        raise LLMConfigurationError(LOCAL_AI_DISABLED_MESSAGE)
    return base_url
