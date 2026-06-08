from __future__ import annotations

import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

from diag.agents.registry import list_agents
from diag.ai.config import API_PROVIDER_NAMES, assert_api_provider_name, normalize_provider_name, resolve_provider_config
from diag.ai.doctor import doctor_provider, list_models
from diag.ai.errors import LLMConfigurationError
from diag.ai.remote_url_validator import LOCAL_AI_DISABLED_MESSAGE, validate_remote_api_url
from diag.core.models import CommandResult, RiskLevel
from diag.engine.context_compactor import compact_messages
from diag.engine.chat_router import route_chat
from diag.engine.event_stream import EventStream
from diag.engine.fast_router import is_known_ops_task, is_process_query, route_fast_path, should_call_api_for_input
from diag.engine.latency_trace import LatencyTrace
from diag.engine.resource_analysis import analyze_process_rows, analyze_resource_snapshot
from diag.engine.resource_schema import resource_event_payload
from diag.engine.session_manager import EngineSession, EngineSessionManager
from diag.engine.summary_builder import build_report_summary, build_run_summary
from diag.engine.telemetry_doctor import telemetry_doctor
from diag.engine.streaming import emit_assistant_stream
from diag.permissions.approval import StaticApprovalProvider
from diag.permissions.sandbox_profiles import get_sandbox_profile, list_sandbox_profiles
from diag.planner.intent import infer_task
from diag.planner.plan_builder import build_plan
from diag.runtime.command_runner import run_command_with_policy
from diag.plugins.loader import PluginLoader
from diag.runtime.agent_loop import AgentLoop
from diag.tools.registry import build_default_registry
from diag.utils.config_loader import deep_merge, load_config, read_config_file
from diag.utils.env_vars import get_env_var
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
            "run.summary": self.run_summary,
            "approval.resolve": self.approval_resolve,
            "raw.show": self.raw_show,
            "report.generate": self.report_generate,
            "resources.snapshot": self.resources_snapshot,
            "resources.analyze": self.resources_analyze,
            "telemetry.doctor": self.telemetry_doctor,
            "latency.trace": self.latency_trace,
            "cancel": self.cancel,
            "process.list_top_cpu": self.process_list_top_cpu,
            "process.list_top_memory": self.process_list_top_memory,
            "process.inspect": self.process_inspect,
            "process.tree": self.process_tree,
            "process.kill_term": self.process_kill_term,
            "process.kill_kill": self.process_kill_kill,
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
            "permissions.list": self.permissions_list,
            "permissions.set": self.permissions_set,
            "tools.list": self.tools_list,
            "agents.list": self.agents_list,
            "context.compact": self.context_compact,
            "doctor.full": self.doctor_full,
            "usage.summary": self.usage_summary,
            "session.info": self.session_info,
            "session.clear": self.session_clear,
        }
        try:
            handler = handlers[method]
        except KeyError as exc:
            raise ValueError(f"Unknown method: {method}") from exc
        started = time.perf_counter()
        try:
            return handler(params)
        finally:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            self.sessions.current().last_latency_ms = elapsed_ms

    def session_start(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.start(params)
        if session.mode.value == "demo" and session.provider is None:
            session.provider = "mock"
            session.model = session.model or "mock-diagnosis-v1"
        elif session.provider is None:
            try:
                config = resolve_provider_config(profile=session.profile)
                session.provider = config.name
                session.model = session.model or config.model
            except ValueError:
                pass
        payload = self._session_payload(session)
        payload.update(_engine_ready_payload())
        self.events.emit("SessionStarted", payload)
        self.events.emit("EngineReady", payload)
        self.events.emit("TelemetryStatus", {"sampler_status": "starting", "session_id": session.session_id})
        return payload

    def chat_message(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        trace = LatencyTrace()
        session.responding = True
        text = str(params.get("text") or "")
        session.user_input = text or session.user_input
        session.messages.append({"role": "user", "content": text})
        self.events.emit("UserMessage", {"session_id": session.session_id, "content": text})

        route_started = time.perf_counter()
        route = route_chat(text)
        fast = route_fast_path(text)
        trace.fast_router_ms = int((time.perf_counter() - route_started) * 1000)
        trace.api_call_count = 0

        if route.intent == "greeting":
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "你好，我是 OpsPilot。你可以直接描述故障，或输入 /help 查看命令；我会先给计划和可选操作，不会擅自执行。", actions=[action("配置 API", "/config api"), action("查看帮助", "/help")]))
        if is_process_query(text):
            focus = "memory" if _looks_like_memory_query(text) else "cpu"
            result = self.process_list_top_memory({"session_id": session.session_id}) if focus == "memory" else self.process_list_top_cpu({"session_id": session.session_id})
            message = result.get("text") or "Process sample refreshed."
            return self._finish_reply(session, trace, self._assistant_reply(session, "process_query", str(message), actions=list(result.get("actions") or _process_action_cards(result.get("items")))))
        if is_known_ops_task(text) and fast.fast and route.intent not in {"evidence_question", "report_request", "raw_request", "plugin_request"}:
            local_started = time.perf_counter()
            plan = self.plan_create({"session_id": session.session_id, "input": text})
            trace.local_plan_ms = int((time.perf_counter() - local_started) * 1000)
            message = "我先给出本地诊断计划和 Action Cards；不会等待远程 API。需要深入分析时再输入 /refine。"
            reply = self._assistant_reply(session, route.intent, message, actions=[action("执行诊断", "/run"), action("查看资源", "/resources"), action("查看进程", "/process")])
            reply["plan"] = plan
            return self._finish_reply(session, trace, reply)
        if route.intent == "api_config":
            provider_hint = _provider_hint(text)
            if provider_hint == "blocked_local_ai":
                return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "OpsPilot 已禁用本地 AI。请配置远程 API；真实 key 只放环境变量。", actions=[action("配置远程 API", "/config api"), action("模型检查", "/model doctor")]))
            self.config_api_start({"session_id": session.session_id, "provider": provider_hint})
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "可以，我会打开可视化 API 向导。真实 key 只读取环境变量，不写入配置文件。", actions=[action("开始配置 API", "/config api"), action("模型检查", "/model doctor")]))
        if route.intent == "model_config":
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "OpsPilot 是 API-only。请配置远程 API；mock 只用于 demo/test。", actions=[action("模型检查", "/model doctor"), action("配置 API", "/config api")]))
        if route.intent == "execute_request":
            if session.current_plan is None:
                local_started = time.perf_counter()
                plan = self.plan_create({"session_id": session.session_id, "input": text})
                trace.local_plan_ms = int((time.perf_counter() - local_started) * 1000)
                message = "我先生成了诊断计划。你可以输入 /run 执行；需要授权的步骤仍会先停下来询问。"
                self._assistant_reply(session, route.intent, message, actions=[action("执行诊断", "/run"), action("查看资源", "/resources")])
                return self._finish_reply(session, trace, {"intent": route.intent, "plan": plan, "message": message})
            tool_started = time.perf_counter()
            run_result = self.plan_run({"session_id": session.session_id})
            trace.tool_run_ms = int((time.perf_counter() - tool_started) * 1000)
            return self._finish_reply(session, trace, {"intent": route.intent, "run": run_result})
        if route.intent == "evidence_question":
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, self._answer_from_evidence(session), actions=[action("查看报告", "/report"), action("显示原始输出", "/raw")]))
        if route.intent == "report_request":
            result = self.report_generate({"session_id": session.session_id})
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, _report_message(result), actions=[action("执行诊断", "/run")]))
        if route.intent == "raw_request":
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "原始输出默认折叠。输入 /raw 可以展开或再次折叠。", actions=[action("展开原始输出", "/raw")]))
        if route.intent == "plugin_request":
            return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "插件可以查看、启用或禁用，但不能绕过 ToolRegistry 和权限策略。", actions=[action("查看插件", "/plugin")]))
        if route.intent == "fault_description":
            local_started = time.perf_counter()
            plan = self.plan_create({"session_id": session.session_id, "input": text})
            trace.local_plan_ms = int((time.perf_counter() - local_started) * 1000)
            message = "我会先生成本地诊断计划，不会立即执行。确认后输入 /run。"
            self._assistant_reply(session, route.intent, message, actions=[action("执行诊断", "/run"), action("配置 API", "/config api")])
            return self._finish_reply(session, trace, {"intent": route.intent, "plan": plan, "message": message})

        if should_call_api_for_input(text):
            trace.api_call_count = 1
            trace.fallback_reason = "remote_refine_deferred"
        return self._finish_reply(session, trace, self._assistant_reply(session, route.intent, "我还不确定你要诊断什么。可以描述故障现象，或输入 /config api 配置远程模型。", actions=[action("配置 API", "/config api"), action("查看帮助", "/help")]))

    def plan_create(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        text = str(params.get("input") or session.user_input or session.task)
        session.user_input = text
        explicit_task = params.get("task")
        task_hint = str(explicit_task) if explicit_task else None
        session.task = infer_task(text, task_hint)
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
        started = time.perf_counter()
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
            sandbox_profile=session.sandbox_profile,
        )
        session.last_outcome = outcome
        session.evidence = [item.to_dict() for item in outcome.evidence]
        usage = getattr(outcome, "resource_usage", {}) or {}
        session.api_calls += int(usage.get("ai_calls", 0))
        session.api_latency_ms += int(usage.get("api_latency_ms", 0))
        if usage.get("fallback_reason"):
            session.fallback_reason = str(usage.get("fallback_reason"))
        session.commands_executed += int(usage.get("commands_executed", 0))
        session.output_bytes += int(usage.get("total_output_bytes", 0))
        session.latency_trace["tool_run_ms"] = int((time.perf_counter() - started) * 1000)
        return {"session_id": session.session_id, "risk": outcome.risk_level, "markdown_path": outcome.markdown_path, "json_path": outcome.json_path}

    def run_summary(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        started = time.perf_counter()
        summary = build_run_summary(session.last_outcome)
        session.latency_trace["local_summary_ms"] = int((time.perf_counter() - started) * 1000)
        text = str(summary.get("text") or "")
        if text:
            session.messages.append({"role": "assistant", "content": text, "actions": summary.get("actions", [])})
            self.events.emit(
                "AssistantMessage",
                {
                    "session_id": session.session_id,
                    "content": text,
                    "intent": "run_summary",
                    "actions": summary.get("actions", []),
                },
            )
        return summary

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
        summary = build_report_summary(session.last_outcome)
        return {
            "markdown_path": session.last_outcome.markdown_path,
            "json_path": session.last_outcome.json_path,
            "text": summary.get("text"),
            "message": summary.get("message"),
            "actions": summary.get("actions", []),
        }

    def resources_snapshot(self, params: dict[str, Any]) -> dict[str, Any]:
        current = self.sessions.get(params.get("session_id")) if params.get("session_id") else self.sessions.current()
        raw_snapshot = current.resource_sampler.sample()
        if raw_snapshot.get("sampler_status") == "error":
            self.events.emit("TelemetryError", {"error": raw_snapshot.get("sampler_error") or "telemetry error", "session_id": current.session_id})
        snapshot = resource_event_payload(raw_snapshot)
        current.last_resource_snapshot = snapshot
        current.frontend_resource_received = True
        snapshot["session"] = {
            "sandbox_profile": current.sandbox_profile,
            "latency_ms": current.last_latency_ms,
            "api_calls": current.api_calls,
            "api_latency_ms": current.api_latency_ms,
            "fallback_reason": current.fallback_reason,
            "estimated_tokens": current.estimated_tokens,
            "commands_executed": current.commands_executed,
            "output_bytes": current.output_bytes,
            "latency_trace": current.latency_trace,
            "responding": current.responding,
        }
        self.events.emit("ResourceUpdated", snapshot)
        return snapshot

    def resources_analyze(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        focus = str(params.get("focus") or "overview")
        snapshot = session.last_resource_snapshot or self.resources_snapshot({"session_id": session.session_id})
        return analyze_resource_snapshot(snapshot, focus=focus)

    def telemetry_doctor(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        snapshot = session.last_resource_snapshot or self.resources_snapshot({"session_id": session.session_id})
        return telemetry_doctor(snapshot, frontend_received=session.frontend_resource_received)

    def latency_trace(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        trace = dict(session.latency_trace)
        text = "\n".join(f"{key}: {value}" for key, value in trace.items())
        return {"text": text, "trace": trace}

    def cancel(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        session.cancelled_generation += 1
        session.responding = False
        session.fallback_reason = "cancelled"
        session.latency_trace["fallback_reason"] = "cancelled"
        self.events.emit("AssistantMessage", {"session_id": session.session_id, "content": "已取消当前后台响应；你可以继续输入。", "intent": "cancel", "actions": [action("查看延迟", "/latency"), action("查看资源", "/resources")]})
        return {"cancelled": True, "text": "已取消当前后台响应；你可以继续输入。"}

    def process_list_top_cpu(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        snapshot = resource_event_payload(session.resource_sampler.sample())
        items = snapshot.get("top_cpu_processes", [])
        session.last_resource_snapshot = snapshot
        analysis = analyze_process_rows(items if isinstance(items, list) else [], focus="cpu", snapshot=snapshot)
        return {"items": items, "text": analysis["text"], "analysis": analysis, "actions": analysis["actions"], "api_call_count": 0}

    def process_list_top_memory(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        snapshot = resource_event_payload(session.resource_sampler.sample())
        items = snapshot.get("top_memory_processes", [])
        session.last_resource_snapshot = snapshot
        analysis = analyze_process_rows(items if isinstance(items, list) else [], focus="memory", snapshot=snapshot)
        return {"items": items, "text": analysis["text"], "analysis": analysis, "actions": analysis["actions"], "api_call_count": 0}

    def process_inspect(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        pid = _validate_pid(params.get("pid"))
        result = run_command_with_policy(f"ps -fp {pid}", session.target, session.mode, session.sandbox_profile, emit=self.events.callback())
        return _command_result_payload(result, "Process inspected.")

    def process_tree(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        pid = _validate_pid(params.get("pid"))
        result = run_command_with_policy(f"pstree -ap {pid}", session.target, session.mode, session.sandbox_profile, emit=self.events.callback())
        return _command_result_payload(result, "Process tree collected.")

    def process_kill_term(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        pid = _validate_pid(params.get("pid"))
        blocked = _blocked_process_reason(pid)
        if blocked:
            self.events.emit(
                "ApprovalRequired",
                {"action": "process.kill_term", "target": f"PID {pid}", "command": f"kill -TERM {pid}", "risk_level": "blocked", "sandbox_profile": session.sandbox_profile, "reason": blocked},
            )
            return {"blocked": True, "text": f"Blocked: {blocked}", "risk": "blocked"}
        provider = StaticApprovalProvider(True, "Approved from frontend") if bool(params.get("approved")) else None
        result = run_command_with_policy(f"kill -TERM {pid}", session.target, session.mode, session.sandbox_profile, risk=RiskLevel.LOW_RISK, approval_provider=provider, emit=self.events.callback())
        if result.skipped:
            return {"approval_required": True, "text": f"Approval required before sending SIGTERM to PID {pid}.", "command": result.command, "risk": result.risk_level}
        return _command_result_payload(result, "Sent SIGTERM. Recheck the process status in about 3 seconds.")

    def process_kill_kill(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        pid = _validate_pid(params.get("pid"))
        reason = _blocked_process_reason(pid) or "SIGKILL is blocked by default; use SIGTERM with approval first."
        self.events.emit(
            "ApprovalRequired",
            {"action": "process.kill_kill", "target": f"PID {pid}", "command": f"kill -9 {pid}", "risk_level": "blocked", "sandbox_profile": session.sandbox_profile, "reason": reason},
        )
        return {"blocked": True, "text": f"Blocked: {reason}", "risk": "blocked"}

    def model_list(self, _params: dict[str, Any]) -> dict[str, Any]:
        config = load_config()
        providers = config.get("providers", {})
        allowed = API_PROVIDER_NAMES | {"mock"}
        sanitized = {name: dict(data) for name, data in providers.items() if isinstance(data, dict) and name in allowed}
        for data in sanitized.values():
            env_name = data.get("api_key_env")
            if env_name:
                data["api_key_env_present"] = bool(get_env_var(str(env_name)))
        return {"text": list_models(), "providers": sanitized, "default": providers.get("default")}

    def model_doctor(self, params: dict[str, Any]) -> dict[str, Any]:
        provider = params.get("provider")
        return {"text": doctor_provider(str(provider) if provider else None)}

    def model_set(self, params: dict[str, Any]) -> dict[str, Any]:
        spec = str(params.get("model") or "")
        if ":" not in spec:
            raise ValueError("model.set expects provider:model")
        provider, model = spec.split(":", 1)
        provider = normalize_provider_name(provider)
        assert_api_provider_name(provider)
        if _contains_local_ai_term(model):
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
        patch = {"providers": {"default": provider, provider: {"model": model}}, "profiles": {"default": {"provider": provider, "model": model}}}
        self._write_local_patch(patch)
        return {"provider": provider, "model": model}

    def config_get(self, _params: dict[str, Any]) -> dict[str, Any]:
        config = load_config()
        providers = config.get("providers", {})
        for value in providers.values():
            if isinstance(value, dict) and value.get("api_key_env"):
                value["api_key_env_present"] = bool(get_env_var(str(value.get("api_key_env"))))
        return config

    def config_patch(self, params: dict[str, Any]) -> dict[str, Any]:
        patch = params.get("patch")
        if not isinstance(patch, dict):
            raise ValueError("config.patch requires object patch")
        _validate_config_patch_api_only(patch)
        self._write_local_patch(patch)
        return {"saved": str(self._local_path())}

    def config_api_start(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        provider = normalize_provider_name(str(params.get("provider") or load_config().get("providers", {}).get("default") or "deepseek"))
        if provider == "blocked_local_ai":
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
        assert_api_provider_name(provider)
        preset = _provider_defaults(provider)
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
        provider = normalize_provider_name(str(params.get("provider") or "deepseek"))
        if provider == "blocked_local_ai":
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
        assert_api_provider_name(provider)
        preset = _provider_defaults(provider)
        session.config_flow.update({"provider": provider, "type": preset["type"], "base_url": preset.get("base_url", ""), "model": preset.get("model", ""), "api_key_env": preset.get("api_key_env", "")})
        return {"flow": dict(session.config_flow)}

    def config_api_set_base_url(self, params: dict[str, Any]) -> dict[str, Any]:
        value = str(params.get("base_url") or params.get("value") or "")
        if value:
            try:
                validate_remote_api_url(value)
            except LLMConfigurationError as exc:
                raise ValueError(str(exc)) from exc
        return self._set_config_flow_value(params, "base_url")

    def config_api_set_model(self, params: dict[str, Any]) -> dict[str, Any]:
        value = str(params.get("model") or params.get("value") or "")
        if _contains_local_ai_term(value):
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
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
        model = str(session.config_flow.get("model") or patch.get("profiles", {}).get("default", {}).get("model") or "")
        session.provider = str(provider)
        session.model = model
        self.events.emit("SessionStarted", self._session_payload(session))
        return {"saved": str(self._local_path()), "provider": provider, "model": model, "api_key_env": env_name, "message": f"已保存 {provider}:{model} 配置，当前会话已切换。真实 key 只读取环境变量 {env_name}，不会写入配置文件。"}
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

    def permissions_list(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        profile = get_sandbox_profile(session.sandbox_profile)
        return {"current": profile.name, "description": profile.description, "profiles": list_sandbox_profiles()}

    def permissions_set(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        profile = get_sandbox_profile(str(params.get("profile") or "safe-read"))
        session.sandbox_profile = profile.name
        self.events.emit("SessionStarted", self._session_payload(session))
        return {"current": profile.name, "description": profile.description}

    def tools_list(self, _params: dict[str, Any]) -> dict[str, Any]:
        tools = build_default_registry().list()
        return {"tools": [{"name": tool.name, "description": tool.description, "risk": tool.risk.value, "scenes": list(tool.scenes)} for tool in tools]}

    def agents_list(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        return {"agents": list_agents(session.sandbox_profile)}

    def context_compact(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        result = compact_messages(session.messages)
        session.messages = list(result["messages"])
        return result

    def doctor_full(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        profile = get_sandbox_profile(session.sandbox_profile)
        text = "\n".join(
            [
                "API:",
                doctor_provider(),
                "",
                f"Sandbox: {profile.name} - {profile.description}",
                f"Tools: {len(build_default_registry().list())} registered",
                f"Plugins: {len(PluginLoader().discover().list())} discovered",
            ]
        )
        return {"text": text}

    def usage_summary(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        return {
            "text": f"api_calls={session.api_calls} estimated_tokens={session.estimated_tokens} commands={session.commands_executed} output_bytes={session.output_bytes} latency_ms={session.last_latency_ms}",
            "api_calls": session.api_calls,
            "api_latency_ms": session.api_latency_ms,
            "fallback_reason": session.fallback_reason,
            "estimated_tokens": session.estimated_tokens,
            "commands_executed": session.commands_executed,
            "output_bytes": session.output_bytes,
            "latency_ms": session.last_latency_ms,
            "api_latency_ms": session.api_latency_ms,
            "fallback_reason": session.fallback_reason,
            "latency_trace": session.latency_trace,
        }

    def session_info(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        return {"text": str(self._session_payload(session)), "session": self._session_payload(session)}

    def session_clear(self, params: dict[str, Any]) -> dict[str, Any]:
        session = self.sessions.get(params.get("session_id"))
        session.messages = []
        session.current_plan = None
        session.evidence = []
        return {"message": "conversation cleared; config preserved"}

    def _assistant_reply(self, session: EngineSession, intent: str, content: str, actions: list[dict[str, str]] | None = None) -> dict[str, Any]:
        last_user_content = next((str(message.get("content") or "") for message in reversed(session.messages) if message.get("role") == "user"), content)
        fast = route_fast_path(last_user_content)
        emit_assistant_stream(self.events.emit, session.session_id, content)
        payload = {"session_id": session.session_id, "content": content, "intent": intent, "actions": actions or []}
        session.messages.append({"role": "assistant", "content": content, "actions": actions or []})
        self.events.emit("AssistantMessage", payload)
        return {"intent": intent, "message": content, "actions": actions or [], "fast_path": fast.fast}


    def _finish_reply(self, session: EngineSession, trace: LatencyTrace, result: dict[str, Any]) -> dict[str, Any]:
        session.responding = False
        trace.mark_total()
        session.latency_trace = trace.to_dict()
        session.last_latency_ms = int(session.latency_trace.get("total_turn_ms") or session.last_latency_ms)
        if trace.fallback_reason:
            session.fallback_reason = trace.fallback_reason
        return result

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
        provider = normalize_provider_name(str(flow.get("provider") or "deepseek"))
        if provider == "blocked_local_ai" or str(flow.get("type") or "") == "blocked":
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
        assert_api_provider_name(provider)
        provider_config = {"type": str(flow.get("type") or "openai-compatible"), "model": str(flow.get("model") or ""), "timeout": 30, "max_tokens": 1024}
        if _contains_local_ai_term(provider_config["model"]):
            raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
        if flow.get("base_url"):
            try:
                validate_remote_api_url(str(flow["base_url"]))
            except LLMConfigurationError as exc:
                raise ValueError(str(exc)) from exc
            provider_config["base_url"] = str(flow["base_url"])
        if flow.get("api_key_env"):
            provider_config["api_key_env"] = str(flow["api_key_env"])
        return {"providers": {"default": provider, provider: provider_config}, "profiles": {"default": {"provider": provider, "model": provider_config["model"]}}}

    def _session_payload(self, session: EngineSession) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "target": session.target,
            "mode": session.mode.value,
            "task": session.task,
            "provider": session.provider,
            "model": session.model,
            "sandbox_profile": session.sandbox_profile,
            "latency_ms": session.last_latency_ms,
        }

    def _local_path(self) -> Path:
        return project_root() / "configs" / "local.yaml"

    def _write_local_patch(self, patch: dict[str, Any]) -> None:
        path = self._local_path()
        current = read_config_file(path)
        merged = deep_merge(current, patch)
        path.write_text(_to_yaml(merged), encoding="utf-8")


def action(label: str, command: str) -> dict[str, str]:
    return {"label": label, "command": command}


def _engine_ready_payload() -> dict[str, Any]:
    try:
        import psutil  # type: ignore

        psutil_available = True
    except Exception:
        psutil_available = False
    return {
        "cwd": os.getcwd(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "psutil_available": psutil_available,
        "project_root": str(project_root()),
    }


def _process_action_cards(value: Any) -> list[dict[str, str]]:
    rows = value if isinstance(value, list) else []
    actions: list[dict[str, str]] = []
    for row in rows[:3]:
        item = row if isinstance(row, dict) else {}
        pid = item.get("pid")
        if pid is None:
            continue
        actions.extend(
            [
                action(f"Inspect {pid}", f"/process inspect {pid}"),
                action(f"Show tree {pid}", f"/process tree {pid}"),
                action(f"SIGTERM {pid}", f"/process term {pid}"),
                action("Refresh", "/process"),
            ]
        )
    return actions or [action("Refresh processes", "/process"), action("Telemetry doctor", "/monitor doctor")]


def _looks_like_memory_query(text: str) -> bool:
    normalized = text.strip().lower()
    return any(word in normalized for word in ["内存", "memory", "mem", "rss"])


def _provider_hint(text: str) -> str:
    lowered = text.lower()
    if _contains_local_ai_term(lowered) or "localhost" in lowered or "127.0.0.1" in lowered:
        return "blocked_local_ai"
    if "deepseek" in lowered or "deep seek" in lowered:
        return "deepseek"
    if "gemini" in lowered:
        return "gemini"
    if "anthropic" in lowered or "claude" in lowered:
        return "anthropic"
    if "openai" in lowered:
        return "openai"
    return "openai_compatible"


def _provider_preset(provider: str) -> dict[str, str]:
    presets = {
        "openai": {"type": "openai", "base_url": "https://api.openai.com/v1", "model": "gpt-4.1-mini", "api_key_env": "OPENAI_API_KEY"},
        "anthropic": {"type": "anthropic", "base_url": "https://api.anthropic.com", "model": "claude-3-5-haiku-latest", "api_key_env": "ANTHROPIC_API_KEY"},
        "gemini": {"type": "openai-compatible", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-1.5-flash", "api_key_env": "GEMINI_API_KEY"},
        "deepseek": {"type": "openai-compatible", "base_url": "https://api.deepseek.com/v1", "model": "deepseekv4", "api_key_env": "DEEPSEEK_API_KEY"},
        "openai_compatible": {"type": "openai-compatible", "base_url": "https://api.example.com/v1", "model": "api-compatible-model", "api_key_env": "OPENAI_COMPATIBLE_API_KEY"},
        "custom": {"type": "openai-compatible", "base_url": "", "model": "", "api_key_env": "CUSTOM_API_KEY"},
        "blocked_local_ai": {"type": "blocked", "base_url": "", "model": "", "api_key_env": ""},
    }
    return presets.get(provider, {"type": "openai-compatible", "base_url": "", "model": "", "api_key_env": "OPENAI_COMPATIBLE_API_KEY"})


def _provider_defaults(provider: str) -> dict[str, str]:
    defaults = dict(_provider_preset(provider))
    data = load_config().get("providers", {}).get(provider, {})
    if isinstance(data, dict):
        for key in ("type", "base_url", "model", "api_key_env"):
            if data.get(key) is not None:
                defaults[key] = str(data.get(key))
    return defaults


def _contains_local_ai_term(value: str) -> bool:
    lowered = value.lower()
    return any(word in lowered for word in ["ol" + "lama", "v" + "llm", "l" + "lama.cpp", "l" + "lama_cpp", "本地模型", "离线模型", "local model", "off" + "line"])


def _validate_config_patch_api_only(patch: dict[str, Any]) -> None:
    providers = patch.get("providers")
    if not isinstance(providers, dict):
        return
    default_provider = providers.get("default")
    if default_provider:
        assert_api_provider_name(normalize_provider_name(str(default_provider)))
    for name, data in providers.items():
        if name == "default":
            continue
        assert_api_provider_name(normalize_provider_name(str(name)))
        if isinstance(data, dict):
            provider_type = str(data.get("type") or "").lower()
            if any(marker in provider_type for marker in ["ol" + "lama", "v" + "llm", "l" + "lama", "local", "off" + "line"]):
                raise ValueError("OpsPilot 已禁用本地 AI，避免消耗本机 CPU/GPU/内存。请配置远程 API。")
            if data.get("base_url"):
                try:
                    validate_remote_api_url(str(data["base_url"]))
                except LLMConfigurationError as exc:
                    raise ValueError(str(exc)) from exc


def _report_message(result: dict[str, Any]) -> str:
    path = result.get("markdown_path")
    if path:
        return f"报告已生成：{path}"
    return str(result.get("message") or "报告还没有生成。先输入 /run 执行诊断。")


def _validate_pid(value: Any) -> int:
    try:
        pid = int(str(value or "").strip())
    except ValueError as exc:
        raise ValueError("process action requires a numeric PID") from exc
    if pid <= 0:
        raise ValueError("process action requires a positive PID")
    return pid


def _blocked_process_reason(pid: int) -> str | None:
    if pid == 1:
        return "PID 1/system init is protected."
    if pid == os.getpid():
        return "OpsPilot engine process is protected."
    try:
        import psutil  # type: ignore

        proc = psutil.Process(pid)
        name = (proc.name() or "").lower()
        username = (proc.username() or "").lower()
        cmdline = " ".join(proc.cmdline()).lower()
        if username in {"root", "system", "local system", "nt authority\\system"}:
            return "root/system owned processes are protected."
        if "opspilot" in name or "opspilot" in cmdline:
            return "OpsPilot processes are protected."
    except Exception:
        return None
    return None


def _command_result_payload(result: CommandResult, success_message: str) -> dict[str, Any]:
    output = (result.stdout or result.stderr or "").strip()
    text = success_message if result.return_code == 0 and not result.skipped else f"Command returned rc={result.return_code}: {result.stderr or result.stdout}".strip()
    if output:
        text = f"{text}\n{output[:1200]}"
    return {"text": text, "result": result.to_dict(), "risk": result.risk_level}


def _format_process_rows(value: Any, title: str) -> str:
    rows = value if isinstance(value, list) else []
    lines = [title]
    if not rows:
        return f"{title}\nNo process sample yet"
    for index, row in enumerate(rows[:8], start=1):
        item = row if isinstance(row, dict) else {}
        memory = item.get("memory_mb", item.get("memory_percent", 0))
        cpu = item.get("normalized_cpu_percent", item.get("cpu_percent", 0))
        raw = item.get("raw_cpu_percent", cpu)
        lines.append(f"[{index}] PID {item.get('pid', '?')} {item.get('name', '?')} CPU {cpu}% raw {raw}% MEM {memory}")
    return "\n".join(lines)


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
