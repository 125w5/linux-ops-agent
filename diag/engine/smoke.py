from __future__ import annotations

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


def run_engine_smoke() -> tuple[bool, str]:
    events: list[str] = []
    methods = EngineMethods(EngineSessionManager(), EventStream(lambda line: events.append(line)))
    session = methods.dispatch("session.start", {})
    if not session.get("session_id"):
        return False, "session.start did not return session_id"
    snapshot = methods.dispatch("resources.snapshot", {"session_id": session["session_id"]})
    if snapshot.get("event") != "ResourceUpdated":
        return False, "resources.snapshot did not return ResourceUpdated schema"
    doctor = methods.dispatch("telemetry.doctor", {"session_id": session["session_id"]})
    if "schema validation" not in str(doctor.get("text", "")):
        return False, "telemetry.doctor did not report schema validation"
    return True, f"engine smoke ok session={session['session_id']} sampler={snapshot.get('sampler_status')}"
