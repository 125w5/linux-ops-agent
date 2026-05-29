from __future__ import annotations

from collections.abc import Callable

from diag.analyzers.cpu_analyzer import analyze_cpu
from diag.analyzers.disk_analyzer import analyze_disk
from diag.analyzers.service_analyzer import analyze_service
from diag.analyzers.ssh_log_analyzer import analyze_ssh_failures
from diag.core.models import CommandResult, DiagnosisOutcome
from diag.executor.local_executor import LocalExecutor
from diag.hooks.after_command import AfterCommandTranscriptHook
from diag.hooks.before_command import BeforeCommandSafetyHook
from diag.hooks.events import AFTER_COMMAND, BEFORE_COMMAND
from diag.hooks.hook_manager import HookManager
from diag.permissions.mode import PermissionMode
from diag.permissions.policy import PermissionDecision, PermissionPolicy
from diag.planner.plan_builder import build_plan
from diag.reports.json_report import write_json_report
from diag.reports.markdown_report import write_markdown_report
from diag.runtime.context import RuntimeContext
from diag.runtime.session import RuntimeSession
from diag.runtime.transcript import Transcript
from diag.storage.database import HistoryStore
from diag.tools.command_tool import CommandTool
from diag.tools.registry import build_default_registry
from diag.utils.paths import database_path, report_dir, transcript_dir


StageCallback = Callable[[int, int, str], None]


class AgentLoop:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        user_input: str,
        target: str,
        task_type: str,
        permission_mode: PermissionMode,
        service: str = "nginx",
        stage: StageCallback | None = None,
    ) -> DiagnosisOutcome:
        stage = stage or (lambda _index, _total, _message: None)
        registry = build_default_registry()

        stage(1, 6, "Start runtime session")
        session = RuntimeSession(user_input=user_input, target=target, task_type=task_type, permission_mode=permission_mode)
        transcript = Transcript(session.session_id)
        transcript.append_user_input(user_input)

        executor = LocalExecutor(timeout_seconds=self.timeout_seconds, demo=permission_mode == PermissionMode.DEMO)
        hook_manager = HookManager()
        hook_manager.register(BEFORE_COMMAND, BeforeCommandSafetyHook())
        hook_manager.register(AFTER_COMMAND, AfterCommandTranscriptHook())
        context = RuntimeContext(
            session=session,
            transcript=transcript,
            registry=registry,
            permission_policy=PermissionPolicy(permission_mode),
            hook_manager=hook_manager,
            executor=executor,
            command_tool=CommandTool(executor),
        )

        stage(2, 6, "Build tool-based diagnosis plan")
        plan = build_plan(user_input, target, task_type, registry=registry, service=service)
        transcript.append_plan(plan)
        outcome = DiagnosisOutcome.start(user_input, plan)
        outcome.session_id = session.session_id
        outcome.started_at = session.started_at

        stage(3, 6, "Run command lifecycle hooks and collectors")
        results: list[CommandResult] = []
        for step in plan.steps:
            decisions = context.hook_manager.run(BEFORE_COMMAND, context, step)
            decision = decisions[-1] if decisions else PermissionDecision(False, step.risk, "No permission decision")
            if not decision.allowed:
                result = CommandResult(
                    command=step.command,
                    target=target,
                    stdout="",
                    stderr=decision.reason,
                    return_code=126,
                    duration_ms=0,
                    risk_level=decision.risk_level.value,
                    skipped=True,
                )
            else:
                result = context.command_tool.run(step, target, decision.risk_level.value)
            results.append(result)
            context.hook_manager.run(AFTER_COMMAND, context, step, result)
        outcome.results = results

        stage(4, 6, "Analyze evidence")
        if task_type == "disk":
            evidence, causes, suggestions, risk_level = analyze_disk(results)
        elif task_type == "cpu":
            evidence, causes, suggestions, risk_level = analyze_cpu(results)
        elif task_type == "service":
            evidence, causes, suggestions, risk_level = analyze_service(results, service=service)
        elif task_type == "ssh-failure":
            evidence, causes, suggestions, risk_level = analyze_ssh_failures(results)
        else:
            evidence, causes, suggestions, risk_level = [], [f"No analyzer for task {task_type}"], [], "info"
        outcome.evidence = evidence
        outcome.root_causes = causes
        outcome.suggestions = suggestions
        outcome.risk_level = risk_level
        transcript.append_evidence(evidence)

        stage(5, 6, "Write reports and transcript")
        session.close()
        outcome.ended_at = session.ended_at or outcome.ended_at
        md_path = write_markdown_report(outcome, report_dir())
        json_path = write_json_report(outcome, report_dir())
        outcome.markdown_path = str(md_path)
        outcome.json_path = str(json_path)
        transcript.append_report_path(outcome.markdown_path, outcome.json_path)
        transcript_path = transcript.write(transcript_dir())
        outcome.suggestions.append(f"Transcript recorded at {transcript_path}")

        stage(6, 6, "Save diagnosis history")
        HistoryStore(database_path()).save(outcome)
        return outcome
