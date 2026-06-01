from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from diag.ai.doctor import doctor_provider, list_models
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
        payload = self._session_payload(session)
        self.events.emit("SessionStarted", payload)
        return payload

    def chat_message(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        text = str(params.get("text") or "")
        session.user_input = text or session.user_input
        session.messages.append({"role": "user", "content": text})
        self.events.emit("UserMessage", {"session_id": session.session_id, "content": text})
        intent = self._classify(text, session)
        if intent == "explain":
            return self._assistant_reply(session, intent, self._explain(session))
        if intent == "evidence":
            return self._assistant_reply(session, intent, self._answer_from_evidence(session))
        plan = self.plan_create({"session_id": session.session_id, "input": text})
        message = "我已经生成诊断计划。可以继续追问，也可以输入 /run 执行。" if intent == "plan" else "你要求执行，我会先生成计划，并在安全模式允许时开始运行。"
        self._assistant_reply(session, intent, message)
        if intent == "execute":
            run_result = self.plan_run({"session_id": session.session_id})
            return {"intent": intent, "plan": plan, "run": run_result}
        return {"intent": intent, "plan": plan, "message": message}

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
            return {"markdown_path": None, "json_path": None, "message": "Report pending"}
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

    def _assistant_reply(self, session: EngineSession, intent: str, content: str) -> dict[str, Any]:
        session.messages.append({"role": "assistant", "content": content})
        self.events.emit("AssistantMessage", {"session_id": session.session_id, "content": content})
        return {"intent": intent, "message": content}

    def _classify(self, text: str, session: EngineSession) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["为什么", "解释", "说明", "what", "why", "explain"]):
            return "explain"
        if any(word in lowered for word in ["证据", "刚才", "上次", "evidence"]):
            return "evidence"
        if any(word in lowered for word in ["执行", "运行", "检查一下", "run", "execute"]):
            return "execute" if session.mode.value in {"demo", "readonly"} else "plan"
        return "plan"

    def _explain(self, session: EngineSession) -> str:
        return f"当前目标是 {session.target} 的 {session.task} 只读诊断。你可以描述现象，我会先生成计划；只有 /run 或明确请求执行时才运行工具。"

    def _answer_from_evidence(self, session: EngineSession) -> str:
        if not session.evidence:
            return "当前会话还没有证据。你可以先描述故障生成计划，再用 /run 执行。"
        return "上次证据摘要：\n" + "\n".join(f"- {item.get('content', '')}" for item in session.evidence[:5])

    def _session_payload(self, session: EngineSession) -> dict[str, Any]:
        return {"session_id": session.session_id, "target": session.target, "mode": session.mode.value, "task": session.task, "provider": session.provider, "model": session.model}

    def _local_path(self) -> Path:
        return project_root() / "configs" / "local.yaml"

    def _write_local_patch(self, patch: dict[str, Any]) -> None:
        path = self._local_path()
        current = read_config_file(path)
        merged = deep_merge(current, patch)
        path.write_text(_to_yaml(merged), encoding="utf-8")


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
