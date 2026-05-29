from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class HookExecutionError(RuntimeError):
    pass


@dataclass
class HookManager:
    _hooks: dict[str, list[Callable[..., Any]]] = field(default_factory=dict)

    def register(self, event: str, hook: Callable[..., Any]) -> None:
        self._hooks.setdefault(event, []).append(hook)

    def run(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        results: list[Any] = []
        for hook in self._hooks.get(event, []):
            try:
                results.append(hook(*args, **kwargs))
            except Exception as exc:
                hook_name = getattr(hook, "__class__", type(hook)).__name__
                raise HookExecutionError(f"Hook {hook_name} failed during {event}: {exc}") from exc
        return results
