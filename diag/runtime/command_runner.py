from __future__ import annotations

from collections.abc import Callable
from typing import Any

from diag.core.models import CommandResult, DiagnosisStep, RiskLevel
from diag.executor.local_executor import LocalExecutor
from diag.hooks.after_command import AfterCommandTranscriptHook
from diag.hooks.before_command import BeforeCommandSafetyHook
from diag.hooks.events import AFTER_COMMAND, BEFORE_COMMAND
from diag.hooks.hook_manager import HookManager
from diag.permissions.approval import ApprovalProvider
from diag.permissions.mode import PermissionMode
from diag.permissions.policy import PermissionPolicy
from diag.runtime.context import RuntimeContext
from diag.runtime.session import RuntimeSession
from diag.runtime.transcript import Transcript
from diag.tools.command_tool import CommandTool
from diag.tools.registry import build_default_registry


Emit = Callable[[str, dict[str, Any]], None]


def run_command_with_policy(
    command: str,
    target: str,
    mode: PermissionMode,
    sandbox_profile: str,
    *,
    risk: RiskLevel = RiskLevel.SAFE_READONLY,
    demo: bool = False,
    approval_provider: ApprovalProvider | None = None,
    emit: Emit | None = None,
) -> CommandResult:
    emit = emit or (lambda _event, _payload: None)
    session = RuntimeSession(user_input=command, target=target, task_type="process", permission_mode=mode)
    transcript = Transcript(session.session_id)
    registry = build_default_registry()
    executor = LocalExecutor(timeout_seconds=10, demo=demo)
    hook_manager = HookManager()
    hook_manager.register(BEFORE_COMMAND, BeforeCommandSafetyHook())
    hook_manager.register(AFTER_COMMAND, AfterCommandTranscriptHook())
    context = RuntimeContext(
        session=session,
        transcript=transcript,
        registry=registry,
        permission_policy=PermissionPolicy(mode, approval_provider=approval_provider, sandbox_profile=sandbox_profile),
        hook_manager=hook_manager,
        executor=executor,
        command_tool=CommandTool(executor),
    )
    step = DiagnosisStep(id="process.command", name="process command", command=command, risk=risk)
    decisions = hook_manager.run(BEFORE_COMMAND, context, step)
    decision = decisions[-1] if decisions else PermissionPolicy(mode, approval_provider=approval_provider, sandbox_profile=sandbox_profile).evaluate(command, preset_risk=risk)
    if decision.requires_confirmation:
        emit("ApprovalRequired", {"action": "process", "command": command, "risk_level": decision.risk_level.value, "sandbox_profile": sandbox_profile, "reason": decision.reason, "target": target})
    if not decision.allowed:
        result = CommandResult(command, target, "", decision.reason, 126, 0, decision.risk_level.value, skipped=True)
        if decision.requires_confirmation:
            emit("ApprovalResolved", {"action": "process", "command": command, "approved": False, "reason": decision.reason})
        emit("ToolFinished", {"step_id": step.id, "command": command, "status": 126, "stdout_bytes": 0})
        return result
    emit("ToolStarted", {"step_id": step.id, "command": command, "tool_name": "process"})
    result = context.command_tool.run(step, target, decision.risk_level.value)
    if decision.requires_confirmation:
        emit("ApprovalResolved", {"action": "process", "command": command, "approved": True, "reason": decision.reason})
    hook_manager.run(AFTER_COMMAND, context, step, result)
    emit("ToolFinished", {"step_id": step.id, "command": command, "status": result.return_code, "stdout_bytes": len(result.stdout.encode("utf-8"))})
    return result
