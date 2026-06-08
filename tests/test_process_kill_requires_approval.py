import io
import json
import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class ProcessKillRequiresApprovalTests(unittest.TestCase):
    def test_sigterm_requires_approval_in_admin_confirm(self) -> None:
        output = io.StringIO()
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda line: output.write(line + "\n")))
        session = methods.session_start({"mode": "confirm", "sandbox_profile": "admin-confirm"})

        result = methods.process_kill_term({"session_id": session["session_id"], "pid": "999999"})
        events = [json.loads(line)["event"] for line in output.getvalue().splitlines() if line.strip()]

        self.assertTrue(result["approval_required"])
        self.assertIn("ApprovalRequired", events)

    def test_sigkill_is_blocked_and_not_approvable(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "confirm", "sandbox_profile": "admin-confirm"})

        result = methods.process_kill_kill({"session_id": session["session_id"], "pid": "999999"})

        self.assertTrue(result["blocked"])
        self.assertIn("SIGKILL", result["text"])


if __name__ == "__main__":
    unittest.main()
