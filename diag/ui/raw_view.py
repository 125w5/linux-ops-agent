from __future__ import annotations

from diag.core.models import CommandResult


def render_raw_results(results: list[CommandResult]) -> str:
    lines: list[str] = []
    for result in results:
        flags: list[str] = []
        if result.skipped:
            flags.append("skipped")
        if result.truncated:
            flags.append("truncated")
        suffix = f" ({', '.join(flags)})" if flags else ""
        lines.append(f"$ {result.command}{suffix}")
        lines.append(f"return_code={result.return_code} duration_ms={result.duration_ms} risk={result.risk_level}")
        if result.stdout:
            lines.append(result.stdout.rstrip())
        if result.stderr:
            lines.append("stderr:")
            lines.append(result.stderr.rstrip())
    return "\n".join(lines)
