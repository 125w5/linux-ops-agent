from __future__ import annotations

import threading
from collections.abc import Callable

from diag.core.models import DiagnosisOutcome
from diag.dashboard.system_monitor import SystemMonitor
from diag.permissions.approval import ApprovalDecision, ApprovalProvider, ApprovalRequest
from diag.permissions.mode import PermissionMode
from diag.planner.intent import infer_task
from diag.planner.plan_builder import build_plan
from diag.plugins.loader import PluginLoader
from diag.runtime.agent_loop import AgentLoop
from diag.tools.registry import build_default_registry
from diag.workbench.context import WorkbenchOptions
from diag.workbench.live_renderer import WorkbenchRenderer
from diag.workbench.session import WorkbenchSession
from diag.workbench.state import WorkbenchState


class WorkbenchApprovalProvider(ApprovalProvider):
    def __init__(self, state: WorkbenchState, on_pending: Callable[[], None] | None = None) -> None:
        self.state = state
        self.on_pending = on_pending

    def request(self, request: ApprovalRequest) -> ApprovalDecision:
        with self.state.approval_condition:
            self.state.approval.command = request.command
            self.state.approval.reason = request.reason
            self.state.approval.pending = True
            self.state.approval.decision = None
            self.state.add_message("agent", f"Approval required: {request.command}")
            if self.on_pending:
                self.on_pending()
            while self.state.approval.decision is None and not self.state.exit_requested:
                self.state.approval_condition.wait(timeout=0.2)
            approved = bool(self.state.approval.decision)
            self.state.approval.pending = False
            reason = "Approved from workbench" if approved else "Denied from workbench"
            self.state.add_message("agent", reason)
            return ApprovalDecision(approved, reason)


class WorkbenchController:
    def __init__(
        self,
        options: WorkbenchOptions,
        state: WorkbenchState,
        session: WorkbenchSession,
        renderer: WorkbenchRenderer,
        output_func=print,
    ) -> None:
        self.options = options
        self.state = state
        self.session = session
        self.renderer = renderer
        self.output_func = output_func
        self.monitor = SystemMonitor(on_sample=self._on_resource_sample)
        self._run_thread: threading.Thread | None = None

    def start(self) -> None:
        self.monitor.sample_once()
        self.monitor.start()
        self.state.add_message("agent", "Workbench ready. 输入 /help 查看命令。")

    def stop(self) -> None:
        self.state.exit_requested = True
        with self.state.approval_condition:
            if self.state.approval.pending and self.state.approval.decision is None:
                self.state.approval.decision = False
                self.state.approval_condition.notify_all()
        if self._run_thread and self._run_thread.is_alive():
            self._run_thread.join(timeout=2)
        self.monitor.stop()
        self.session.close()
        path = self.session.write()
        self.output_func(f"Workbench transcript: {path}")

    def plan(self, text: str | None = None) -> str:
        if text is not None:
            self.state.user_input = text
        user_input = self.state.user_input or self.state.task_type
        self.state.task_type = infer_task(user_input, self.state.task_type)
        registry = build_default_registry()
        self.state.current_plan = build_plan(user_input, self.state.target, self.state.task_type, registry=registry, service=self.state.service)
        self.state.dashboard.apply(
            "PlanCreated",
            {
                "task_type": self.state.current_plan.task_type,
                "target": self.state.current_plan.target,
                "steps": [
                    {"id": step.id, "name": step.name, "command": step.command, "risk": step.risk.value, "tool_name": step.tool_name}
                    for step in self.state.current_plan.steps
                ],
            },
        )
        self.state.add_message("user", user_input)
        self.state.add_message("agent", f"Plan generated for {self.state.task_type}. 输入 /run 执行。")
        return f"Plan generated: {len(self.state.current_plan.steps)} step(s)"

    def run(self) -> str:
        if self.state.running:
            return "A diagnosis is already running."
        if self.state.current_plan is None:
            self.plan(self.state.user_input or self.state.task_type)
        self.state.running = True
        self.state.status = "running"
        self._run_thread = threading.Thread(target=self._run_agent_loop, name="opspilot-workbench-run", daemon=True)
        self._run_thread.start()
        return "Run started."

    def approve(self) -> str:
        with self.state.approval_condition:
            if not self.state.approval.pending:
                return "No approval is pending."
            self.state.approval.decision = True
            self.session.append_event("approval", {"command": self.state.approval.command, "approved": True})
            self.state.approval_condition.notify_all()
        return "Approved."

    def deny(self) -> str:
        with self.state.approval_condition:
            if not self.state.approval.pending:
                return "No approval is pending."
            self.state.approval.decision = False
            self.session.append_event("approval", {"command": self.state.approval.command, "approved": False})
            self.state.approval_condition.notify_all()
        return "Denied."

    def plugins(self) -> str:
        records = PluginLoader().discover().list()
        if not records:
            return "No plugins found."
        return "\n".join(f"- {record.manifest.name}: {'enabled' if record.enabled else 'disabled'}" for record in records)

    def _run_agent_loop(self) -> None:
        provider = WorkbenchApprovalProvider(self.state, on_pending=lambda: self.renderer.render(self.output_func))
        try:
            outcome = AgentLoop(timeout_seconds=self.options.timeout).run(
                user_input=self.state.user_input or self.state.task_type,
                target=self.state.target,
                task_type=self.state.task_type,
                permission_mode=self.state.mode,
                service=self.state.service,
                provider=self.state.provider,
                model=self.state.model,
                profile=self.state.profile,
                skill=self.state.skill,
                use_ssh=self.options.use_ssh,
                style=self.state.style,
                stage=None,
                event_callback=self._event_callback,
                approval_provider=provider,
            )
            self._complete(outcome)
        except Exception as exc:
            self.state.add_message("agent", f"Run failed: {exc}")
            self.session.append_event("run_error", {"error": str(exc)})
        finally:
            self.state.running = False
            self.state.status = "idle"
            self.renderer.render(self.output_func)

    def _complete(self, outcome: DiagnosisOutcome) -> None:
        self.state.dashboard.complete_from_outcome(outcome)
        self.state.outcome_report_path = outcome.markdown_path or ""
        self.state.outcome_json_path = outcome.json_path or ""
        self.state.risk = outcome.risk_level
        self.state.add_message("agent", f"Run complete. Report: {self.state.outcome_report_path}")

    def _event_callback(self, event_type: str, payload: dict) -> None:
        self.state.apply_event(event_type, payload)
        self.session.append_event(event_type, payload)
        self.renderer.render(self.output_func)

    def _on_resource_sample(self, snapshot: dict) -> None:
        self.state.set_resources(snapshot)
