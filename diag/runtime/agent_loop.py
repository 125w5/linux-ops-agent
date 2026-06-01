from __future__ import annotations

from collections.abc import Callable

from diag.analyzers.cpu_analyzer import analyze_cpu
from diag.analyzers.disk_analyzer import analyze_disk
from diag.analyzers.service_analyzer import analyze_service
from diag.analyzers.ssh_log_analyzer import analyze_ssh_failures
from diag.ai.model_router import ModelRouter
from diag.core.models import CommandResult, DiagnosisOutcome
from diag.executor.local_executor import LocalExecutor
from diag.executor.ssh_executor import SSHExecutor
from diag.hooks.after_command import AfterCommandTranscriptHook
from diag.hooks.before_command import BeforeCommandSafetyHook
from diag.hooks.events import AFTER_COMMAND, BEFORE_COMMAND
from diag.hooks.hook_manager import HookManager
from diag.permissions.mode import PermissionMode
from diag.permissions.approval import ApprovalProvider
from diag.permissions.policy import PermissionDecision, PermissionPolicy
from diag.plugins.loader import PluginLoader
from diag.planner.plan_builder import build_plan
from diag.reports.json_report import write_json_report
from diag.reports.markdown_report import write_markdown_report
from diag.resources.budget import load_resource_budget
from diag.resources.command_budget import command_allowed
from diag.resources.limiter import apply_output_limits
from diag.resources.profiler import Profiler
from diag.resources.token_budget import estimate_tokens, fit_text_to_token_budget
from diag.resources.usage import ResourceUsage
from diag.runtime.context import RuntimeContext
from diag.runtime.session import RuntimeSession
from diag.runtime.transcript import Transcript
from diag.skills.loader import SkillLoader
from diag.skills.selector import select_skill
from diag.storage.database import HistoryStore
from diag.tools.command_tool import CommandTool
from diag.tools.registry import build_default_registry
from diag.utils.paths import database_path, report_dir, transcript_dir


StageCallback = Callable[[int, int, str], None]
EventCallback = Callable[[str, dict], None]


class AgentLoop:
    def __init__(self, timeout_seconds: int = 15) -> None:
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        user_input: str,
        target: str,
        task_type: str,
        permission_mode: PermissionMode,
        service: str = "nginx",
        provider: str | None = None,
        model: str | None = None,
        profile: str | None = None,
        skill: str | None = None,
        use_ssh: bool = False,
        style: str | None = None,
        stage: StageCallback | None = None,
        event_callback: EventCallback | None = None,
        approval_provider: ApprovalProvider | None = None,
    ) -> DiagnosisOutcome:
        stage = stage or (lambda _index, _total, _message: None)
        emit = event_callback or (lambda _event_type, _payload: None)
        profiler = Profiler()
        budget = load_resource_budget()
        usage = ResourceUsage()
        registry = build_default_registry()
        router = ModelRouter(provider=provider, model=model, profile=profile, force_mock=permission_mode == PermissionMode.DEMO)

        stage(1, 6, "Start runtime session")
        session = RuntimeSession(user_input=user_input, target=target, task_type=task_type, permission_mode=permission_mode)
        transcript = Transcript(session.session_id)
        transcript.append_user_input(user_input)
        emit(
            "SessionStarted",
            {
                "session_id": session.session_id,
                "target": target,
                "task_type": task_type,
                "mode": permission_mode.value,
                "provider": router.config.name,
                "model": router.config.model,
            },
        )

        executor_timeout = min(self.timeout_seconds, budget.command_timeout_seconds)
        if use_ssh:
            executor = SSHExecutor(timeout_seconds=executor_timeout, demo=permission_mode == PermissionMode.DEMO)
        else:
            executor = LocalExecutor(timeout_seconds=executor_timeout, demo=permission_mode == PermissionMode.DEMO)
        hook_manager = HookManager()
        hook_manager.register(BEFORE_COMMAND, BeforeCommandSafetyHook())
        hook_manager.register(AFTER_COMMAND, AfterCommandTranscriptHook())
        plugin_records = PluginLoader().load_enabled(registry, hook_manager)
        if plugin_records:
            transcript.append_event(
                "plugins_loaded",
                {"plugins": [{"name": record.manifest.name, "valid": record.valid, "errors": record.errors} for record in plugin_records]},
            )
        context = RuntimeContext(
            session=session,
            transcript=transcript,
            registry=registry,
            permission_policy=PermissionPolicy(permission_mode, approval_provider=approval_provider),
            hook_manager=hook_manager,
            executor=executor,
            command_tool=CommandTool(executor),
        )

        stage(2, 6, "Build tool-based diagnosis plan")
        skill_registry = SkillLoader().load()
        selected_skill = select_skill(skill_registry, task_type, requested=skill)
        if selected_skill:
            transcript.append_event(
                "skill_selected",
                {
                    "name": selected_skill.name,
                    "risk_max": selected_skill.risk_max,
                    "scenes": selected_skill.scenes,
                    "description": selected_skill.description,
                },
            )
        def call_ai(label: str, text: str, fn):
            if usage.ai_calls >= budget.ai.max_calls_per_session:
                transcript.append_event("ai_budget_skipped", {"role": label, "reason": "max AI calls reached"})
                return None
            limited_text, truncated = fit_text_to_token_budget(text, router.config.max_tokens)
            if truncated:
                transcript.append_event(
                    "ai_input_limited",
                    {"role": label, "estimated_tokens": estimate_tokens(text), "max_tokens": router.config.max_tokens},
                )
            usage.ai_calls += 1
            return fn(limited_text)

        try:
            ai_plan = call_ai("planner", user_input, lambda text: router.planner(text, [tool.name for tool in registry.list()]))
            transcript.append_event("ai_planner", ai_plan)
        except Exception as exc:
            transcript.append_event("ai_planner_error", {"error": str(exc)})
        plan = build_plan(user_input, target, task_type, registry=registry, service=service)
        transcript.append_plan(plan)
        emit(
            "PlanCreated",
            {
                "task_type": plan.task_type,
                "target": plan.target,
                "steps": [{"id": step.id, "name": step.name, "command": step.command, "risk": step.risk.value, "tool_name": step.tool_name} for step in plan.steps],
            },
        )
        outcome = DiagnosisOutcome.start(user_input, plan)
        outcome.session_id = session.session_id
        outcome.started_at = session.started_at

        stage(3, 6, "Run command lifecycle hooks and collectors")
        results: list[CommandResult] = []
        for index, step in enumerate(plan.steps):
            usage.commands_started += 1
            emit("ToolStarted", {"step_id": step.id, "command": step.command, "tool_name": step.tool_name})
            if not command_allowed(index, budget):
                result = CommandResult(
                    command=step.command,
                    target=target,
                    stdout="",
                    stderr="Skipped by command budget",
                    return_code=124,
                    duration_ms=0,
                    risk_level="blocked",
                    skipped=True,
                )
                usage.commands_skipped += 1
                result = apply_output_limits(result, budget, usage)
                results.append(result)
                context.hook_manager.run(AFTER_COMMAND, context, step, result)
                emit(
                    "ToolFinished",
                    {
                        "step_id": step.id,
                        "command": result.command,
                        "tool_name": step.tool_name,
                        "status": "skipped",
                        "truncated": result.truncated,
                        "stdout_bytes": len(result.stdout.encode("utf-8")),
                    },
                )
                continue
            decisions = context.hook_manager.run(BEFORE_COMMAND, context, step)
            decision = decisions[-1] if decisions else PermissionDecision(False, step.risk, "No permission decision")
            if decision.requires_confirmation:
                emit("ApprovalRequired", {"step_id": step.id, "command": step.command, "risk_level": decision.risk_level.value, "reason": decision.reason})
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
                usage.commands_skipped += 1
                if decision.requires_confirmation:
                    emit("ApprovalResolved", {"step_id": step.id, "approved": False, "reason": decision.reason})
            else:
                result = context.command_tool.run(step, target, decision.risk_level.value)
                usage.commands_executed += 1
                if decision.requires_confirmation:
                    emit("ApprovalResolved", {"step_id": step.id, "approved": True, "reason": decision.reason})
            result = apply_output_limits(result, budget, usage)
            results.append(result)
            context.hook_manager.run(AFTER_COMMAND, context, step, result)
            emit(
                "ToolFinished",
                {
                    "step_id": step.id,
                    "command": result.command,
                    "tool_name": step.tool_name,
                    "status": "skipped" if result.skipped else result.return_code,
                    "truncated": result.truncated,
                    "stdout_bytes": len(result.stdout.encode("utf-8")),
                },
            )
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
        for record in plugin_records:
            for name, analyzer in (record.analyzers or {}).items():
                try:
                    plugin_result = analyzer(tuple(results), tuple(evidence))
                    if isinstance(plugin_result, tuple):
                        plugin_evidence, plugin_suggestions = plugin_result
                    else:
                        plugin_evidence, plugin_suggestions = plugin_result, []
                    evidence.extend(list(plugin_evidence or []))
                    suggestions.extend(str(item) for item in (plugin_suggestions or []))
                    transcript.append_event("plugin_analyzer", {"plugin": record.manifest.name, "analyzer": name, "status": "ok"})
                except Exception as exc:
                    transcript.append_event("plugin_analyzer_error", {"plugin": record.manifest.name, "analyzer": name, "error": str(exc)})
        outcome.evidence = evidence
        outcome.root_causes = causes
        outcome.suggestions = suggestions
        outcome.risk_level = risk_level
        transcript.append_evidence(evidence)
        emit("EvidenceAdded", {"items": [item.to_dict() for item in evidence]})
        try:
            evidence_text = str([item.to_dict() for item in evidence])
            summary = call_ai("summarizer", evidence_text, lambda text: router.summarizer([{"summary_input": text}]))
            transcript.append_event("ai_summarizer", {"summary": summary})
        except Exception as exc:
            transcript.append_event("ai_summarizer_error", {"error": str(exc)})
        try:
            risk_note = call_ai("risk_reviewer", "session command set", lambda text: router.risk_reviewer(text, outcome.risk_level))
            transcript.append_event("ai_risk_reviewer", {"note": risk_note})
        except Exception as exc:
            transcript.append_event("ai_risk_reviewer_error", {"error": str(exc)})

        stage(5, 6, "Write reports and transcript")
        session.close()
        outcome.ended_at = session.ended_at or outcome.ended_at
        md_path = write_markdown_report(outcome, report_dir(), style=style)
        json_path = write_json_report(outcome, report_dir())
        outcome.markdown_path = str(md_path)
        outcome.json_path = str(json_path)
        transcript.append_report_path(outcome.markdown_path, outcome.json_path)
        emit("ReportWritten", {"markdown_path": outcome.markdown_path, "json_path": outcome.json_path})
        try:
            report_input = f"risk={outcome.risk_level}; causes={outcome.root_causes}; suggestions={outcome.suggestions}"
            polished = call_ai("report_writer", report_input, lambda text: router.report_writer(text))
            transcript.append_event("ai_report_writer", {"note": polished})
        except Exception as exc:
            transcript.append_event("ai_report_writer_error", {"error": str(exc)})
        usage.duration_ms = profiler.elapsed_ms()
        outcome.resource_usage = usage.to_dict()
        transcript.append_event("resource_usage", usage.to_dict())
        emit("ResourceUpdated", usage.to_dict())
        transcript_path = transcript.write(transcript_dir())
        outcome.suggestions.append(f"Transcript recorded at {transcript_path}")

        stage(6, 6, "Save diagnosis history")
        HistoryStore(database_path()).save(outcome)
        emit("SessionEnded", {"session_id": outcome.session_id, "risk_level": outcome.risk_level})
        return outcome
