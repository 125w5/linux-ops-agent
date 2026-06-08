import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class SamplerSessionReuseTests(unittest.TestCase):
    def test_session_reuses_sampler(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.dispatch("session.start", {})
        one = methods.dispatch("resources.snapshot", {"session_id": session["session_id"]})
        two = methods.dispatch("resources.snapshot", {"session_id": session["session_id"]})
        self.assertEqual(one["logical_cpu_count"], two["logical_cpu_count"])
        if one["psutil_available"]:
            self.assertEqual(one["sampler_status"], "warming_up")
            self.assertEqual(two["sampler_status"], "ready")


if __name__ == "__main__":
    unittest.main()
