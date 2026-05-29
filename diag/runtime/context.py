from __future__ import annotations

from dataclasses import dataclass

from diag.executor.local_executor import LocalExecutor
from diag.hooks.hook_manager import HookManager
from diag.permissions.policy import PermissionPolicy
from diag.runtime.session import RuntimeSession
from diag.runtime.transcript import Transcript
from diag.tools.command_tool import CommandTool
from diag.tools.registry import ToolRegistry


@dataclass
class RuntimeContext:
    session: RuntimeSession
    transcript: Transcript
    registry: ToolRegistry
    permission_policy: PermissionPolicy
    hook_manager: HookManager
    executor: LocalExecutor
    command_tool: CommandTool
