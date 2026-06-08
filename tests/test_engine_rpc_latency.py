import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineRpcLatencyTests(unittest.TestCase):
    def test_dispatch_records_latency_on_session(self) -> None:
        sessions = EngineSessionManager()
        methods = EngineMethods(sessions, EventStream(lambda _line: None))

        session = methods.dispatch("session.start", {"mode": "demo"})
        methods.dispatch("resources.snapshot", {"session_id": session["session_id"]})

        self.assertGreaterEqual(sessions.current().last_latency_ms, 0)


if __name__ == "__main__":
    unittest.main()
