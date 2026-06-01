from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatRoute:
    intent: str
    reason: str


def route_chat(text: str) -> ChatRoute:
    normalized = text.strip().lower()
    compact = "".join(normalized.split())
    if not normalized:
        return ChatRoute("unknown", "empty input")
    if compact in {"你好", "您好", "hi", "hello", "hey", "hello!", "hi!"}:
        return ChatRoute("greeting", "greeting only")
    if _has_any(normalized, ["配置 api", "配置api", "api key", "apikey", "openai", "anthropic", "deepseek", "gemini", "base_url", "base url"]):
        return ChatRoute("api_config", "api configuration request")
    if _has_any(normalized, ["模型", "model", "/model", "ollama", "provider"]):
        return ChatRoute("model_config", "model/provider request")
    if normalized.startswith("/run") or _has_any(normalized, ["执行", "运行一下", "跑一下", "开始诊断", "run", "execute"]):
        return ChatRoute("execute_request", "execution request")
    if normalized.startswith("/raw") or _has_any(normalized, ["原始输出", "raw output", "show raw"]):
        return ChatRoute("raw_request", "raw output request")
    if normalized.startswith("/report") or _has_any(normalized, ["报告", "report", "生成总结"]):
        return ChatRoute("report_request", "report request")
    if normalized.startswith("/plugin") or _has_any(normalized, ["插件", "plugin"]):
        return ChatRoute("plugin_request", "plugin request")
    if _has_any(normalized, ["为什么", "解释", "说明", "what", "explain"]):
        return ChatRoute("evidence_question", "explanation request")
    if _has_any(normalized, ["证据", "刚才", "上次", "能删吗", "能不能删", "/proc/kcore", "evidence", "why"]):
        return ChatRoute("evidence_question", "question about evidence or safety")
    if _has_any(normalized, ["磁盘", "cpu", "内存", "服务", "ssh", "nginx", "故障", "异常", "是不是有问题", "变慢", "满了", "disk", "service"]):
        return ChatRoute("fault_description", "fault description")
    return ChatRoute("unknown", "not enough diagnostic intent")


def _has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)
