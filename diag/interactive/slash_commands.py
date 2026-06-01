from __future__ import annotations

from diag.interactive.help_panel import render_help
from diag.interactive.session_state import InteractiveSessionState
from diag.planner.intent import infer_task
from diag.planner.plan_builder import build_plan
from diag.ui.raw_view import render_raw_results
from diag.ui.renderer import render_outcome
from diag.ui.tree import render_plan_tree
from diag.tui.widgets.config_screen import render_config_screen


def plan_from_text(state: InteractiveSessionState, text: str) -> str:
    state.user_input = text
    state.task_type = infer_task(text, None)
    state.plan = build_plan(text, state.target, state.task_type, service=state.service)
    state.status = "planned"
    return "Plan generated. Use /plan to inspect, /run to execute."


def handle_slash_command(state: InteractiveSessionState, command: str, args: str, run_callback) -> tuple[bool, str]:
    if command in {"/exit", "/quit"}:
        state.status = "exiting"
        return True, "Bye."
    if command == "/help":
        return False, render_help()
    if command == "/plan":
        if args:
            return False, plan_from_text(state, args)
        if not state.plan:
            return False, "No plan yet. Type a fault description first."
        return False, render_plan_tree(state.plan)
    if command == "/run":
        if not state.plan:
            if args:
                plan_from_text(state, args)
            else:
                return False, "No plan yet. Type a fault description first."
        outcome = run_callback(state)
        state.outcome = outcome
        state.resource_usage = getattr(outcome, "resource_usage", {}) or {}
        state.status = "completed"
        return False, render_outcome(outcome, view="normal", style=state.style, resources=state.resource_usage)
    if command in {"/approve", "/deny"}:
        state.status = "approval_recorded" if command == "/approve" else "denied"
        return False, f"{command[1:].capitalize()} recorded for pending command flow."
    if command == "/evidence":
        if not state.outcome:
            return False, "No evidence yet. Run the plan first."
        return False, "\n".join(f"- [{item.severity}] {item.content}" for item in state.outcome.evidence)
    if command == "/raw":
        if not state.outcome:
            return False, "No raw output yet. Run the plan first."
        return False, render_raw_results(state.outcome.results)
    if command == "/report":
        if not state.outcome:
            return False, "No report yet. Run the plan first."
        return False, state.outcome.markdown_path or "(report missing)"
    if command == "/status":
        return False, state.describe()
    if command == "/resources":
        if not state.resource_usage:
            return False, "No resource usage yet."
        return False, "\n".join(f"{key}: {value}" for key, value in state.resource_usage.items())
    if command == "/model":
        if args:
            state.model = args
        return False, f"provider={state.provider or 'default'} model={state.model or 'default'}"
    if command == "/style":
        if args:
            state.style = args
        return False, f"style={state.style or 'default'}"
    if command == "/layout":
        return False, f"layout={args or 'default'}"
    if command == "/config":
        return False, render_config_screen()
    if command == "/plugin":
        return False, "Use `python -m diag plugin list` or `python -m diag plugin doctor <name>`."
    if command == "/skill":
        if args:
            state.skill = args
        return False, f"skill={state.skill or 'auto'}"
    if command == "/mode":
        return False, f"mode={state.mode.value}"
    if command == "/history":
        return False, "Input history is available from the current chat session file."
    return False, f"Unknown command: {command}. Use /help."
