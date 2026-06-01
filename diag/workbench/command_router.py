from __future__ import annotations

import os
from typing import Any

from diag.ai.doctor import doctor_provider, list_models
from diag.engine.methods import _to_yaml
from diag.utils.config_loader import deep_merge, load_config, read_config_file
from diag.utils.paths import project_root
from diag.workbench.controller import WorkbenchController
from diag.workbench.slash_commands import help_text, list_commands
from diag.workbench.state import WorkbenchState


class WorkbenchCommandRouter:
    def __init__(self, state: WorkbenchState, controller: WorkbenchController) -> None:
        self.state = state
        self.controller = controller

    def handle(self, text: str) -> str:
        stripped = text.strip()
        if not stripped:
            return ""
        if stripped in {"A", "a"}:
            return self.controller.approve()
        if stripped in {"D", "d"}:
            return self.controller.deny()
        if not stripped.startswith("/"):
            return self._handle_chat(stripped)
        return self._handle_slash(stripped)

    def _handle_chat(self, text: str) -> str:
        intent = self._classify(text)
        if intent == "explain":
            self.state.add_message("user", text)
            message = (
                f"我现在会围绕 {self.state.target} 的 {self.state.task_type} 做只读诊断。"
                "你可以继续描述现象，我会先生成计划；只有你输入 /run 或明确说“执行/运行”时才会开始调用工具。"
            )
            self.state.add_message("agent", message)
            return message
        if intent == "evidence":
            self.state.add_message("user", text)
            items = self.state.dashboard.evidence[:5]
            if not items:
                message = "当前会话还没有证据。你可以先描述问题生成计划，再输入 /run 执行诊断。"
            else:
                message = "最近证据摘要：\n" + "\n".join(f"- {item.get('content', '')}" for item in items)
            self.state.add_message("agent", message)
            return message
        if intent == "execute":
            self.controller.plan(text)
            return self.controller.run()
        return self.controller.plan(text)

    def _handle_slash(self, text: str) -> str:
        name, _, args = text.partition(" ")
        if name == "/":
            return help_text("/")
        if name not in {command.name for command in list_commands("/")}:
            matches = list_commands(name)
            if matches:
                return help_text(name)
            return f"Unknown command: {name}. Type /help."
        if name == "/help":
            return help_text(args.strip() or "/")
        if name == "/plan":
            return self.controller.plan(args.strip() or None)
        if name == "/run":
            return self.controller.run()
        if name == "/raw":
            self.state.raw_expanded = not self.state.raw_expanded
            return "Raw expanded." if self.state.raw_expanded else "Raw folded."
        if name == "/report":
            return self.state.outcome_report_path or self.state.dashboard.report_path or "Report pending."
        if name == "/resources":
            return str(self.state.dashboard.resources or {})
        if name == "/model":
            return self._handle_model(args.strip())
        if name == "/plugin":
            return self.controller.plugins()
        if name == "/config":
            return self._handle_config(args.strip())
        if name == "/approve":
            return self.controller.approve()
        if name == "/deny":
            return self.controller.deny()
        if name == "/exit":
            self.state.exit_requested = True
            return "Bye."
        return f"Unhandled command: {name}"

    def _classify(self, text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["为什么", "解释", "说明", "what", "why", "explain"]):
            return "explain"
        if any(word in lowered for word in ["证据", "刚才", "上次", "evidence"]):
            return "evidence"
        if any(word in lowered for word in ["执行", "运行", "检查一下", "run", "execute"]):
            return "execute"
        return "plan"

    def _handle_model(self, args: str) -> str:
        if not args or args == "current":
            return f"provider={self.state.provider or 'default'} model={self.state.model or 'default'}"
        if args == "list":
            return list_models()
        if args.startswith("doctor"):
            _, _, provider = args.partition(" ")
            return doctor_provider(provider.strip() or None)
        if args.startswith("use "):
            spec = args.removeprefix("use ").strip()
            provider, sep, model = spec.partition(":")
            if not sep or not provider or not model:
                return "用法：/model use provider:model，例如 /model use openai:gpt-4.1-mini"
            self._save_local_patch(
                {
                    "providers": {"default": provider, provider: {"model": model}},
                    "profiles": {"default": {"provider": provider, "model": model}},
                }
            )
            self.state.provider = provider
            self.state.model = model
            return f"已保存默认模型：{provider}:{model}。API key 仍通过环境变量读取，不会写入配置文件。"
        return "可用命令：/model list、/model doctor [provider]、/model use provider:model"

    def _handle_config(self, args: str) -> str:
        if args in {"api", "apis", ""}:
            config = load_config()
            providers = config.get("providers", {})
            lines = [
                "API 配置入口：",
                "1. 用 /model list 查看可用 provider/model。",
                "2. 用 /model doctor [provider] 检查环境变量是否存在。",
                "3. 用 /model use provider:model 切换默认模型。",
                "4. API key 请放在环境变量里，例如 OPENAI_API_KEY，不会写入 configs/local.yaml。",
                "",
                "当前 provider：",
            ]
            for name, value in providers.items():
                if name == "default" or not isinstance(value, dict):
                    continue
                env_name = value.get("api_key_env")
                suffix = f" env={env_name} present={bool(os.environ.get(str(env_name)))}" if env_name else ""
                lines.append(f"- {name}: type={value.get('type', name)} model={value.get('model', '(default)')}{suffix}")
            return "\n".join(lines)
        if args == "show":
            config = load_config()
            return self._sanitize_config(config)
        return "可用命令：/config api、/config show"

    def _save_local_patch(self, patch: dict[str, Any]) -> None:
        path = project_root() / "configs" / "local.yaml"
        current = read_config_file(path)
        merged = deep_merge(current, patch)
        path.write_text(_to_yaml(merged), encoding="utf-8")

    def _sanitize_config(self, config: dict[str, Any]) -> str:
        providers = config.get("providers", {})
        if isinstance(providers, dict):
            for value in providers.values():
                if isinstance(value, dict) and value.get("api_key"):
                    value["api_key"] = "***"
        return _to_yaml(config)
