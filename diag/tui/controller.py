from __future__ import annotations

from dataclasses import dataclass

from diag.permissions.mode import parse_permission_mode
from diag.planner.intent import infer_task
from diag.planner.plan_builder import build_plan
from diag.runtime.agent_loop import AgentLoop
from diag.tui.runtime_bridge import RuntimeEventBridge
from diag.tui.state import TuiState


@dataclass
class PendingApproval:
    command: str
    risk: str
    reason: str
    resolved: bool = False
    approved: bool = False


class TuiController:
    def __init__(self, state: TuiState, bridge: RuntimeEventBridge | None = None) -> None:
        self.state = state
        self.bridge = bridge or RuntimeEventBridge(state)
        self.pending_approval: PendingApproval | None = None
        self.raw_expanded = False

    def plan(self, text: str = "disk", service: str = "nginx") -> None:
        task_type = infer_task(text, text if text in {"disk", "cpu", "service", "ssh-failure", "ssh"} else None)
        plan = build_plan(text, self.state.target, task_type, service=service)
        self.bridge.emit(
            "PlanCreated",
            {"steps": [{"id": step.id, "name": step.name, "command": step.command, "risk": step.risk.value, "tool_name": step.tool_name} for step in plan.steps]},
        )

    def run(self, task: str = "disk", service: str = "nginx") -> None:
        mode = parse_permission_mode(self.state.mode, demo=self.state.mode == "demo")
        AgentLoop().run(
            user_input=task,
            target=self.state.target,
            task_type=infer_task(task, task),
            permission_mode=mode,
            service=service,
            event_callback=self.bridge.callback(),
        )

    def request_approval(self, command: str, risk: str, reason: str) -> PendingApproval:
        self.pending_approval = PendingApproval(command, risk, reason)
        event = "ApprovalRequired" if risk != "blocked" else "ApprovalResolved"
        payload = {"command": command, "risk_level": risk, "reason": reason, "approved": False}
        self.bridge.emit(event, payload)
        return self.pending_approval

    def approve(self) -> bool:
        if not self.pending_approval or self.pending_approval.risk == "blocked":
            return False
        self.pending_approval.resolved = True
        self.pending_approval.approved = True
        self.bridge.emit("ApprovalResolved", {"command": self.pending_approval.command, "approved": True, "reason": "approved in TUI"})
        return True

    def deny(self) -> bool:
        if not self.pending_approval:
            return False
        self.pending_approval.resolved = True
        self.pending_approval.approved = False
        self.bridge.emit("ApprovalResolved", {"command": self.pending_approval.command, "approved": False, "reason": "denied in TUI"})
        return True

    def toggle_raw(self) -> bool:
        self.raw_expanded = not self.raw_expanded
        return self.raw_expanded
