from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from diag.ai.doctor import doctor_provider, list_models
from diag.engine.chat_router import route_chat
from diag.engine.event_stream import EventStream
from diag.engine.session_manager import EngineSession, EngineSessionManager
from diag.planner.intent import infer_task
from diag.planner.plan_builder import build_plan
from diag.plugins.loader import PluginLoader
from diag.runtime.agent_loop import AgentLoop
from diag.tools.registry import build_default_registry
from diag.utils.config_loader import deep_merge, load_config, read_config_file
from diag.utils.paths import project_root


class EngineMethods:
    def __init__(self, sessions: EngineSessionManager, events: EventStream) -> None:
        self.sessions = sessions
        self.events = events

    def dispatch(self, method: str, params: dict[str, Any]) -> Any:
        handlers = {
            "session.start": self.session_start,
            "chat.message": self.chat_message,
            "plan.create": self.plan_create,
            "plan.run": self.plan_run,
            "approval.resolve": self.approval_resolve,
            "raw.show": self.raw_show,
            "report.generate": self.report_generate,
            "resources.snapshot": self.resources_snapshot,
            "model.list": self.model_list,
            "model.doctor": self.model_doctor,
            "model.set": self.model_set,
            "config.get": self.config_get,
            "config.patch": self.config_patch,
            "config.api.start": self.config_api_start,
            "config.api.set_provider": self.config_api_set_provider,
            "config.api.set_base_url": self.config_api_set_base_url,
            "config.api.set_model": self.config_api_set_model,
            "config.api.set_api_key_env": self.config_api_set_api_key_env,
            "config.api.preview": self.config_api_preview,
            "config.api.save": self.config_api_save,
            "plugin.list": self.plugin_list,
            "plugin.enable": self.plugin_enable,
            "plugin.disable": self.plugin_disable,
        }
        try:
            handler = handlers[method]
        except KeyError as exc:
            raise ValueError(f"Unknown method: {method}") from exc
        return handler(params)

    def session_start(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.start(params)
        if session.mode.value == "demo" and session.provider is None:
            session.provider = "mock"
            session.model = session.model or "mock-diagnosis-v1"
        payload = self._session_payload(session)
        self.events.emit("SessionStarted", payload)
        return payload

    def chat_message(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        text = str(params.get("text") or "")
        session.user_input = text or session.user_input
        session.messages.append({"role": "user", "content": text})
        self.events.emit("UserMessage", {"session_id": session.session_id, "content": text})

        route = route_chat(text)
        if route.intent == "greeting":
            return self._assistant_reply(session, route.intent, "你好，我是 OpsPilot。你可以描述故障，我会先解释和规划，不会擅自执行。", actions=[action("配置 API", "/config api"), action("查看帮助", "/help")])
        if route.intent == "api_config":
            self.config_api_start({"session_id": session.session_id, "provider": _provider_hint(text)})
            return self._assistant_reply(session, route.intent, "可以，我会用对话式向导帮你配置 API。真实 key 只放环境变量，不会写入配置文件。", actions=[action("开始配置 API", "/config api"), action("检查模型", "/model doctor")])
        if route.intent == "model_config":
            return self._assistant_reply(session, route.intent, "可以查看、检查或切换模型。默认不会偷偷启用本地 Ollama，除非你主动选择。", actions=[action("模型检查", "/model doctor"), action("配置 API", "/config api")])
        if route.intent == "execute_request":
            if session.current_plan is None:
                plan = self.plan_create({"session_id": session.session_id, "input": text})
                message = "我先生成了诊断计划。你可以输入 /run 执行；在 confirm 模式下仍会等待授权。"
                self._assistant_reply(session, route.intent, message, actions=[action("执行诊断", "/run"), action("查看计划", "/plan")])
                return {"intent": route.intent, "plan": plan, "message": message}
            run_result = self.plan_run({"session_id": session.session_id})
            return {"intent": route.intent, "run": run_result}
        if route.intent == "evidence_question":
            return self._assistant_reply(session, route.intent, self._answer_from_evidence(session), actions=[action("查看报告", "/report"), action("显示原始输出", "/raw")])
        if route.intent == "report_request":
            result = self.report_generate({"session_id": session.session_id})
            return self._assistant_reply(session, route.intent, _report_message(result), actions=[action("执行诊断", "/run")])
        if route.intent == "raw_request":
            return self._assistant_reply(session, route.intent, "原始输出默认折叠。输入 /raw 可以展开或再次折叠。", actions=[action("展开原始输出", "/raw")])
        if route.intent == "plugin_request":
            return self._assistant_reply(session, route.intent, "插件能力可以查看、启用或禁用，但不会绕过 ToolRegistry 和权限策略。", actions=[action("查看插件", "/plugin")])
        if route.intent == "fault_description":
            plan = self.plan_create({"session_id": session.session_id, "input": text})
            message = "我会生成诊断计划，但不会立即执行。确认后输入 /run。"
            self._assistant_reply(session, route.intent, message, actions=[action("执行诊断", "/run"), action("配置 API", "/config api")])
            return {"intent": route.intent, "plan": plan, "message": message}

        return self._assistant_reply(session, route.intent, "我还不确定你要诊断什么。可以描述故障现象，或输入 /config api 配置模型。", actions=[action("配置 API", "/config api"), action("查看帮助", "/help")])

    def plan_create(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        text = str(params.get("input") or session.user_input or session.task)
        session.user_input = text
        session.task = infer_task(text, session.task)
        session.current_plan = build_plan(text, session.target, session.task, registry=build_default_registry(), service=session.service)
        payload = {
            "session_id": session.session_id,
            "task_type": session.current_plan.task_type,
            "target": session.current_plan.target,
            "steps": [
                {"id": step.id, "name": step.name, "command": step.command, "risk": step.risk.value, "tool_name": step.tool_name}
                for step in session.current_plan.steps
            ],
        }
        self.events.emit("PlanCreated", payload)
        return payload

    def plan_run(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        if session.current_plan is None:
            self.plan_create({"session_id": session.session_id, "input": session.user_input or session.task})
        outcome = AgentLoop(timeout_seconds=int(params.get("timeout") or 15)).run(
            user_input=session.user_input or session.task,
            target=session.target,
            task_type=session.task,
            permission_mode=session.mode,
            service=session.service,
            provider=session.provider,
            model=session.model,
            profile=session.profile,
            style=session.style,
            stage=None,
            event_callback=self.events.callback(),
        )
        session.last_outcome = outcome
        session.evidence = [item.to_dict() for item in outcome.evidence]
        return {"session_id": session.session_id, "risk": outcome.risk_level, "markdown_path": outcome.markdown_path, "json_path": outcome.json_path}

    def approval_resolve(self, params: dict[str, Any]) -> dict[str, Any]:
        approved = bool(params.get("approved", False))
        self.events.emit("ApprovalResolved", {"approved": approved, "reason": "Resolved from frontend"})
        return {"approved": approved}

    def raw_show(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        results = session.last_outcome.results if session.last_outcome else []
        return {"items": [result.to_dict() for result in results]}

    def report_generate(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        if not session.last_outcome:
            return {"markdown_path": None, "json_path": None, "message": "报告还没有生成。先输入 /run 执行诊断。"}
        return {"markdown_path": session.last_outcome.markdown_path, "json_path": session.last_outcome.json_path}

    def resources_snapshot(self, _params: dict[str, Any]) -> dict[str, Any]:
        from diag.dashboard.resource_sampler import sample_resources

        snapshot = sample_resources()
        self.events.emit("ResourceUpdated", snapshot)
        return snapshot

    def model_list(self, _params: dict[str, Any]) -> dict[str, Any]:
        config = load_config()
        providers = config.get("providers", {})
        sanitized = {name: dict(data) for name, data in providers.items() if isinstance(data, dict)}
        for data in sanitized.values():
            env_name = data.get("api_key_env")
            if env_name:
                data["api_key_env_present"] = bool(os.environ.get(str(env_name)))
        return {"text": list_models(), "providers": sanitized, "default": providers.get("default")}

    def model_doctor(self, params: dict[str, Any]) -> dict[str, Any]:
        provider = params.get("provider")
        return {"text": doctor_provider(str(provider) if provider else None)}

    def model_set(self, params: dict[str, Any]) -> dict[str, Any]:
        spec = str(params.get("model") or "")
        if ":" not in spec:
            raise ValueError("model.set expects provider:model")
        provider, model = spec.split(":", 1)
        patch = {"providers": {"default": provider, provider: {"model": model}}, "profiles": {"default": {"provider": provider, "model": model}}}
        self._write_local_patch(patch)
        return {"provider": provider, "model": model}

    def config_get(self, _params: dict[str, Any]) -> dict[str, Any]:
        config = load_config()
        providers = config.get("providers", {})
        for value in providers.values():
            if isinstance(value, dict) and value.get("api_key_env"):
                value["api_key_env_present"] = bool(os.environ.get(str(value.get("api_key_env"))))
        return config

    def config_patch(self, params: dict[str, Any]) -> dict[str, Any]:
        patch = params.get("patch")
        if not isinstance(patch, dict):
            raise ValueError("config.patch requires object patch")
        self._write_local_patch(patch)
        return {"saved": str(self._local_path())}

    def config_api_start(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        provider = str(params.get("provider") or "openai-compatible")
        preset = _provider_preset(provider)
        session.config_flow = {
            "provider": provider,
            "type": preset["type"],
            "base_url": params.get("base_url") or preset.get("base_url", ""),
            "model": params.get("model") or preset.get("model", ""),
            "api_key_env": params.get("api_key_env") or preset.get("api_key_env", ""),
        }
        return {"flow": dict(session.config_flow), "next": "set_provider"}

    def config_api_set_provider(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        provider = str(params.get("provider") or "openai-compatible")
        preset = _provider_preset(provider)
        session.config_flow.update({"provider": provider, "type": preset["type"], "base_url": preset.get("base_url", ""), "model": preset.get("model", ""), "api_key_env": preset.get("api_key_env", "")})
        return {"flow": dict(session.config_flow)}

    def config_api_set_base_url(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._set_config_flow_value(params, "base_url")

    def config_api_set_model(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._set_config_flow_value(params, "model")

    def config_api_set_api_key_env(self, params: dict[str, Any]) -> dict[str, Any]:
        key_env = str(params.get("api_key_env") or params.get("value") or "").strip()
        if key_env.startswith("sk-") or key_env.startswith("AIza"):
            raise ValueError("Only env var names are allowed; do not send real API keys")
        params = dict(params)
        params["value"] = key_env
        return self._set_config_flow_value(params, "api_key_env")

    def config_api_preview(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        patch = self._config_flow_patch(session)
        return {"patch": patch, "yaml": _to_yaml(patch)}

    def config_api_save(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        patch = self._config_flow_patch(session)
        self._write_local_patch(patch)
        provider = session.config_flow.get("provider", "provider")
        env_name = session.config_flow.get("api_key_env", "")
        return {"saved": str(self._local_path()), "provider": provider, "api_key_env": env_name, "message": f"已保存 {provider} 配置。请在系统环境变量中设置 {env_name}，不要把真实 key 写入文件。"}

    def plugin_list(self, _params: dict[str, Any]) -> dict[str, Any]:
        records = PluginLoader().discover().list()
        return {"plugins": [{"name": record.manifest.name, "enabled": record.enabled, "valid": record.valid, "errors": record.errors} for record in records]}

    def plugin_enable(self, params: dict[str, Any]) -> dict[str, Any]:
        name = str(params.get("name") or "")
        PluginLoader().enable(name)
        return {"name": name, "enabled": True}

    def plugin_disable(self, params: dict[str, Any]) -> dict[str, Any]:
        name = str(params.get("name") or "")
        PluginLoader().disable(name)
        return {"name": name, "enabled": False}

    def _assistant_reply(self, session: EngineSession, intent: str, content: str, actions: list[dict[str, str]] | None = None) -> dict[str, Any]:
        payload = {"session_id": session.session_id, "content": content, "intent": intent, "actions": actions or []}
        session.messages.append({"role": "assistant", "content": content, "actions": actions or []})
        self.events.emit("AssistantMessage", payload)
        return {"intent": intent, "message": content, "actions": actions or []}

    def _answer_from_evidence(self, session: EngineSession) -> str:
        if not session.evidence:
            return "当前会话还没有证据。先执行诊断后，我会基于证据回答；不会凭空建议删除危险文件。"
        summary = "\n".join(f"- {item.get('content', '')}" for item in session.evidence[:5])
        return "基于最近证据：\n" + summary

    def _set_config_flow_value(self, params: dict[str, Any], key: str) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        if not session.config_flow:
            self.config_api_start({"session_id": session.session_id})
        session.config_flow[key] = str(params.get(key) or params.get("value") or "")
        return {"flow": dict(session.config_flow)}

    def _config_flow_patch(self, session: EngineSession) -> dict[str, Any]:
        if not session.config_flow:
            self.config_api_start({"session_id": session.session_id})
        flow = session.config_flow
        provider = str(flow.get("provider") or "openai-compatible")
        provider_config = {"type": str(flow.get("type") or "openai-compatible"), "model": str(flow.get("model") or ""), "timeout": 30, "max_tokens": 1024}
        if flow.get("base_url"):
            provider_config["base_url"] = str(flow["base_url"])
        if flow.get("api_key_env"):
            provider_config["api_key_env"] = str(flow["api_key_env"])
        return {"providers": {"default": provider, provider: provider_config}, "profiles": {"default": {"provider": provider, "model": provider_config["model"]}}}

    def _session_payload(self, session: EngineSession) -> dict[str, Any]:
        return {"session_id": session.session_id, "target": session.target, "mode": session.mode.value, "task": session.task, "provider": session.provider, "model": session.model}

    def _local_path(self) -> Path:
        return project_root() / "configs" / "local.yaml"

    def _write_local_patch(self, patch: dict[str, Any]) -> None:
        path = self._local_path()
        current = read_config_file(path)
        merged = deep_merge(current, patch)
        path.write_text(_to_yaml(merged), encoding="utf-8")


def action(label: str, command: str) -> dict[str, str]:
    return {"label": label, "command": command}


def _provider_hint(text: str) -> str:
    lowered = text.lower()
    if "deepseek" in lowered:
        return "deepseek"
    if "gemini" in lowered:
        return "gemini"
    if "anthropic" in lowered or "claude" in lowered:
        return "anthropic"
    if "ollama" in lowered:
        return "ollama"
    if "openai" in lowered:
        return "openai"
    return "openai-compatible"


def _provider_preset(provider: str) -> dict[str, str]:
    presets = {
        "openai": {"type": "openai", "base_url": "https://api.openai.com/v1", "model": "gpt-4.1-mini", "api_key_env": "OPENAI_API_KEY"},
        "anthropic": {"type": "anthropic", "base_url": "https://api.anthropic.com", "model": "claude-3-5-haiku-latest", "api_key_env": "ANTHROPIC_API_KEY"},
        "deepseek": {"type": "openai-compatible", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat", "api_key_env": "DEEPSEEK_API_KEY"},
        "gemini": {"type": "openai-compatible", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-1.5-flash", "api_key_env": "GEMINI_API_KEY"},
        "ollama": {"type": "ollama", "base_url": "http://localhost:11434", "model": "llama3.2", "api_key_env": ""},
        "custom": {"type": "openai-compatible", "base_url": "", "model": "", "api_key_env": "CUSTOM_API_KEY"},
    }
    return presets.get(provider, {"type": "openai-compatible", "base_url": "", "model": "", "api_key_env": "OPENAI_COMPATIBLE_API_KEY"})


def _report_message(result: dict[str, Any]) -> str:
    path = result.get("markdown_path")
    if path:
        return f"报告已生成：{path}"
    return str(result.get("message") or "报告还没有生成。先输入 /run 执行诊断。")


def _to_yaml(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_to_yaml(value, indent + 2).rstrip())
        else:
            lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines) + "\n"
