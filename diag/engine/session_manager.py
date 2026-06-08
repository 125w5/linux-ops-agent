from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, utc_now
from diag.dashboard.resource_sampler import ProcessSampler
from diag.engine.latency_trace import empty_latency_trace
from diag.permissions.mode import PermissionMode, parse_permission_mode


@dataclass
class EngineSession:
    session_id: str
    target: str = "localhost"
    mode: PermissionMode = PermissionMode.DEMO
    task: str = "disk"
    service: str = "nginx"
    provider: str | None = None
    model: str | None = None
    profile: str | None = None
    style: str | None = None
    user_input: str = ""
    current_plan: DiagnosisPlan | None = None
    last_outcome: DiagnosisOutcome | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    config_flow: dict[str, Any] = field(default_factory=dict)
    sandbox_profile: str = "safe-read"
    fast_mode: bool = False
    api_calls: int = 0
    api_latency_ms: int = 0
    fallback_reason: str = ""
    estimated_tokens: int = 0
    commands_executed: int = 0
    output_bytes: int = 0
    last_latency_ms: int = 0
    resource_sampler: ProcessSampler = field(default_factory=ProcessSampler)
    last_resource_snapshot: dict[str, Any] = field(default_factory=dict)
    frontend_resource_received: bool = False
    responding: bool = False
    cancelled_generation: int = 0
    latency_trace: dict[str, Any] = field(default_factory=empty_latency_trace)
    started_at: str = field(default_factory=utc_now)


class EngineSessionManager:
    def __init__(self) -> None:
        self.sessions: dict[str, EngineSession] = {}
        self.current_id: str | None = None

    def start(self, params: dict[str, Any]) -> EngineSession:
        session = EngineSession(
            session_id=str(uuid4()),
            target=str(params.get("target") or "localhost"),
            mode=parse_permission_mode(params.get("mode") or "demo", demo=bool(params.get("demo", False))),
            task=str(params.get("task") or "disk"),
            service=str(params.get("service") or "nginx"),
            provider=params.get("provider"),
            model=params.get("model"),
            profile=params.get("profile"),
            style=params.get("style"),
            sandbox_profile=str(params.get("sandbox_profile") or "safe-read"),
        )
        self.sessions[session.session_id] = session
        self.current_id = session.session_id
        return session

    def current(self) -> EngineSession:
        if self.current_id and self.current_id in self.sessions:
            return self.sessions[self.current_id]
        return self.start({})

    def get(self, session_id: str | None) -> EngineSession:
        if session_id and session_id in self.sessions:
            self.current_id = session_id
            return self.sessions[session_id]
        return self.current()
