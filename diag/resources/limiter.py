from __future__ import annotations

from diag.core.models import CommandResult
from diag.resources.budget import ResourceBudget
from diag.resources.output_budget import truncate_text
from diag.resources.usage import ResourceUsage


def apply_output_limits(result: CommandResult, budget: ResourceBudget, usage: ResourceUsage) -> CommandResult:
    stdout, stdout_truncated = truncate_text(result.stdout, budget.max_stdout_bytes_per_command)
    stderr, stderr_truncated = truncate_text(result.stderr, budget.max_stdout_bytes_per_command)
    total_bytes = len(stdout.encode("utf-8")) + len(stderr.encode("utf-8"))
    if usage.total_output_bytes + total_bytes > budget.max_total_output_bytes:
        remaining = max(0, budget.max_total_output_bytes - usage.total_output_bytes)
        stdout, total_truncated = truncate_text(stdout, remaining)
        stdout_truncated = stdout_truncated or total_truncated
    result.stdout = stdout
    result.stderr = stderr
    result.truncated = stdout_truncated or stderr_truncated
    usage.stdout_bytes += len(result.stdout.encode("utf-8"))
    usage.stderr_bytes += len(result.stderr.encode("utf-8"))
    usage.total_output_bytes = usage.stdout_bytes + usage.stderr_bytes
    if result.truncated:
        usage.truncated_results += 1
    return result
