from __future__ import annotations

from diag.core.models import CommandResult, DiagnosisStep
from typing import Protocol


class Executor(Protocol):
    def run(self, command: str, target: str, risk_level: str) -> CommandResult:
        ...


class CommandTool:
    def __init__(self, executor: Executor) -> None:
        self.executor = executor

    def run(self, step: DiagnosisStep, target: str, risk_level: str) -> CommandResult:
        return self.executor.run(step.command, target, risk_level)
