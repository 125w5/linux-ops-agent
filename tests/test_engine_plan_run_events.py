import io
import json
import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EnginePlanRunEventsTests(unittest.TestCase):
    def test_plan_run_streams_tool_evidence_and_report_events(self) -> None:
        output = io.StringIO()
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda line: output.write(line + "\n")))
        session = methods.session_start({"target": "localhost", "mode": "demo", "task": "disk", "style": "student"})

        methods.plan_create({"session_id": session["session_id"], "input": "检查磁盘"})
        result = methods.plan_run({"session_id": session["session_id"], "timeout": 5})

        event_names = [json.loads(line).get("event") for line in output.getvalue().splitlines() if line.strip()]
        self.assertIn("ToolStarted", event_names)
        self.assertIn("ToolFinished", event_names)
        self.assertIn("EvidenceAdded", event_names)
        self.assertIn("ReportWritten", event_names)
        self.assertTrue(result["markdown_path"])


if __name__ == "__main__":
    unittest.main()
