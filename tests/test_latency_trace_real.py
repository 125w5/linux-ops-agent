import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class LatencyTraceRealTests(unittest.TestCase):
    def test_chat_turn_records_trace(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.dispatch("session.start", {})
        methods.dispatch("chat.message", {"session_id": session["session_id"], "text": "hello"})
        trace = methods.dispatch("latency.trace", {"session_id": session["session_id"]})["trace"]
        self.assertIn("fast_router_ms", trace)
        self.assertEqual(trace["api_call_count"], 0)


if __name__ == "__main__":
    unittest.main()
