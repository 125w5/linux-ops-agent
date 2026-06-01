from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StatusLineData:
    session_id: str
    task: str
    target: str
    mode: str
    provider: str
    model: str
    commands_count: int
    duration_ms: int
    stdout_bytes: int
    risk: str
    token_usage: int | None = None
    estimated_cost: float | None = None


def render_statusline(data: StatusLineData, width: int = 200) -> str:
    parts = [
        f"session={data.session_id[:8]}",
        f"task={data.task}",
        f"target={data.target}",
        f"mode={data.mode}",
        f"risk={data.risk}",
        f"model={data.provider}/{data.model}",
        f"cmds={data.commands_count}",
        f"dur={data.duration_ms}ms",
        f"out={data.stdout_bytes}B",
    ]
    if data.token_usage is not None:
        parts.append(f"tokens={data.token_usage}")
    if data.estimated_cost is not None:
        parts.append(f"cost=${data.estimated_cost:.4f}")
    line = " | ".join(parts)
    return line if len(line) <= width else line[: max(0, width - 3)] + "..."


def preview_statusline() -> str:
    return render_statusline(
        StatusLineData(
            session_id="preview-session",
            task="disk",
            target="localhost",
            mode="demo",
            provider="mock",
            model="mock-diagnosis-v1",
            commands_count=5,
            duration_ms=128,
            stdout_bytes=4096,
            risk="warning",
            token_usage=0,
            estimated_cost=0.0,
        )
    )


def statusline_config_text() -> str:
    return "fields: session_id, task, target, mode, provider/model, commands count, duration, stdout bytes, risk, token usage, estimated cost"
