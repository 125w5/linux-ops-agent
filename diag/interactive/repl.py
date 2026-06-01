from __future__ import annotations

from collections.abc import Callable

from diag.interactive.command_parser import parse_interactive_input
from diag.interactive.input_history import InputHistory
from diag.interactive.session_state import InteractiveSessionState
from diag.interactive.slash_commands import handle_slash_command, plan_from_text
from diag.runtime.agent_loop import AgentLoop


def run_interactive_repl(
    state: InteractiveSessionState,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    history = InputHistory()
    output_func("OpsPilot-Linux interactive diagnosis. Type /help for commands, /exit to quit.")

    def run_callback(current: InteractiveSessionState):
        return AgentLoop().run(
            user_input=current.user_input or current.task_type or "",
            target=current.target,
            task_type=current.task_type or "disk",
            permission_mode=current.mode,
            service=current.service,
            provider=current.provider,
            model=current.model,
            profile=current.profile,
            skill=current.skill,
            style=current.style,
        )

    while True:
        try:
            text = input_func("diag> ").strip()
        except EOFError:
            break
        if not text:
            continue
        history.append(text)
        parsed = parse_interactive_input(text)
        if parsed.is_command:
            should_exit, message = handle_slash_command(state, parsed.name, parsed.args, run_callback)
            output_func(message)
            if should_exit:
                break
            continue
        output_func(plan_from_text(state, parsed.args))
    return 0
