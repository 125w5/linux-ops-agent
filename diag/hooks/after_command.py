from __future__ import annotations

from diag.core.models import CommandResult, DiagnosisStep
from diag.runtime.context import RuntimeContext


class AfterCommandTranscriptHook:
    def __call__(self, context: RuntimeContext, step: DiagnosisStep, result: CommandResult) -> None:
        context.transcript.append_command_result(step, result)
