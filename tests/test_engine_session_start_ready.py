import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineSessionStartReadyTests(unittest.TestCase):
    def test_session_start_returns_engine_ready_fields(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        result = methods.dispatch("session.start", {})
        self.assertTrue(result["session_id"])
        self.assertIn("cwd", result)
        self.assertIn("python_executable", result)
        self.assertIn("platform", result)
        self.assertIn("project_root", result)


if __name__ == "__main__":
    unittest.main()
