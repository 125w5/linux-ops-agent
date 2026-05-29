from __future__ import annotations

from diag.core.models import CommandResult, DiagnosisStep
from diag.executor.local_executor import LocalExecutor


class CommandTool:
    def __init__(self, executor: LocalExecutor) -> None:
        self.executor = executor

    def run(self, step: DiagnosisStep, target: str, risk_level: str) -> CommandResult:
        return self.executor.run(step.command, target, risk_level)
