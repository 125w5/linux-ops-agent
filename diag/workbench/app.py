from __future__ import annotations

from collections.abc import Callable

from diag.permissions.mode import parse_permission_mode
from diag.workbench.context import WorkbenchOptions
from diag.workbench.controller import WorkbenchController
from diag.workbench.event_loop import WorkbenchEventLoop
from diag.workbench.live_renderer import WorkbenchRenderer
from diag.workbench.session import WorkbenchSession
from diag.workbench.state import WorkbenchState


def build_workbench(options: WorkbenchOptions, output_func=print) -> WorkbenchEventLoop:
    mode = parse_permission_mode(options.mode, demo=options.demo or options.mode == "demo")
    state = WorkbenchState(
        target=options.target,
        mode=mode,
        task_type=options.task,
        service=options.service,
        provider=options.provider,
        model=options.model,
        profile=options.profile,
        style=options.style,
        skill=options.skill,
    )
    session = WorkbenchSession()
    renderer = WorkbenchRenderer(state)
    controller = WorkbenchController(options, state, session, renderer, output_func=output_func)
    return WorkbenchEventLoop(state, controller, renderer, session, output_func=output_func)


def run_workbench(
    options: WorkbenchOptions,
    input_func: Callable[[str], str] | None = None,
    output_func: Callable[[str], None] = print,
) -> int:
    loop = build_workbench(options, output_func=output_func)
    loop.input.input_func = input_func
    return loop.run()
