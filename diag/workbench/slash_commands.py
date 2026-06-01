from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SlashCommand:
    name: str
    description: str


COMMANDS: tuple[SlashCommand, ...] = (
    SlashCommand("/help", "显示 workbench 命令"),
    SlashCommand("/plan", "为当前输入生成诊断计划"),
    SlashCommand("/run", "执行当前 plan"),
    SlashCommand("/raw", "折叠/展开原始输出摘要"),
    SlashCommand("/report", "显示最近报告路径"),
    SlashCommand("/resources", "显示资源与成本统计"),
    SlashCommand("/model", "模型配置：list、doctor、use provider:model"),
    SlashCommand("/plugin", "显示插件状态"),
    SlashCommand("/config", "配置入口：api、show"),
    SlashCommand("/approve", "批准当前 confirm 请求"),
    SlashCommand("/deny", "拒绝当前 confirm 请求"),
    SlashCommand("/exit", "退出 workbench"),
)


def list_commands(prefix: str = "/") -> list[SlashCommand]:
    return [command for command in COMMANDS if command.name.startswith(prefix)]


def help_text(prefix: str = "/") -> str:
    commands = list_commands(prefix)
    if not commands:
        return f"No commands match {prefix}"
    return "\n".join(f"{command.name:<12} {command.description}" for command in commands)
