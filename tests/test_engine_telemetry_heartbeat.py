import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineTelemetryHeartbeatTests(unittest.TestCase):
    def test_resources_snapshot_returns_schema(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.dispatch("session.start", {})
        snapshot = methods.dispatch("resources.snapshot", {"session_id": session["session_id"]})
        self.assertEqual(snapshot["event"], "ResourceUpdated")
        self.assertIn(snapshot["sampler_status"], {"warming_up", "ready", "error"})
        self.assertIn("memory", snapshot)
        self.assertIn("disk", snapshot)


if __name__ == "__main__":
    unittest.main()
