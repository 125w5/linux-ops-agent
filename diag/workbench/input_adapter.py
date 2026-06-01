from __future__ import annotations

from collections.abc import Callable


class InputAdapter:
    def __init__(self, input_func: Callable[[str], str] | None = None) -> None:
        self.input_func = input_func
        self._prompt_session = None
        if input_func is None:
            try:
                from prompt_toolkit import PromptSession

                self._prompt_session = PromptSession()
            except Exception:
                self._prompt_session = None

    def prompt(self, prompt_text: str = "diag> ") -> str:
        if self.input_func:
            return self.input_func(prompt_text)
        if self._prompt_session is not None:
            return self._prompt_session.prompt(prompt_text)
        return input(prompt_text)
