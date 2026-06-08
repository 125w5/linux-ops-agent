import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class CancelApiRequestTests(unittest.TestCase):
    def test_cancel_clears_responding(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.dispatch("session.start", {})
        current = methods.sessions.current()
        current.responding = True
        methods.dispatch("cancel", {"session_id": session["session_id"]})
        self.assertFalse(current.responding)
        self.assertEqual(current.fallback_reason, "cancelled")


if __name__ == "__main__":
    unittest.main()
