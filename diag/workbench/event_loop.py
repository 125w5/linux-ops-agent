from __future__ import annotations

from collections.abc import Callable

from diag.workbench.command_router import WorkbenchCommandRouter
from diag.workbench.controller import WorkbenchController
from diag.workbench.input_adapter import InputAdapter
from diag.workbench.live_renderer import WorkbenchRenderer
from diag.workbench.session import WorkbenchSession
from diag.workbench.state import WorkbenchState


class WorkbenchEventLoop:
    def __init__(
        self,
        state: WorkbenchState,
        controller: WorkbenchController,
        renderer: WorkbenchRenderer,
        session: WorkbenchSession,
        input_func: Callable[[str], str] | None = None,
        output_func: Callable[[str], None] = print,
    ) -> None:
        self.state = state
        self.controller = controller
        self.renderer = renderer
        self.session = session
        self.input = InputAdapter(input_func)
        self.output_func = output_func
        self.router = WorkbenchCommandRouter(state, controller)

    def run(self) -> int:
        self.controller.start()
        self.renderer.render(self.output_func)
        try:
            while not self.state.exit_requested:
                try:
                    text = self.input.prompt("diag> ")
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.session.append_event("interrupt", {"reason": "KeyboardInterrupt"})
                    self.output_func("")
                    continue
                response = self.router.handle(text)
                if response:
                    self.output_func(response)
                for message in self.state.messages[-2:]:
                    self.session.append_message(message)
                if not self.state.exit_requested:
                    self.renderer.render(self.output_func)
        finally:
            self.controller.stop()
        return 0
