import json
import tempfile
import unittest
from pathlib import Path

from diag.core.models import CommandResult, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.runtime.transcript import Transcript


class RuntimeTests(unittest.TestCase):
    def test_transcript_records_required_sections(self) -> None:
        transcript = Transcript("session-1")
        plan = DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "Check df", "df -h")])
        transcript.append_user_input("disk full")
        transcript.append_plan(plan)
        transcript.append_command_result(plan.steps[0], CommandResult("df -h", "localhost", "ok", "", 0, 1, "safe_readonly"))
        transcript.append_evidence([EvidenceItem("df", "usage", "/ is 93%", "warning")])
        transcript.append_report_path("report.md", "report.json")

        with tempfile.TemporaryDirectory() as tmp:
            path = transcript.write(Path(tmp))
            data = json.loads(path.read_text(encoding="utf-8"))

        event_types = [event["type"] for event in data["events"]]
        self.assertIn("user_input", event_types)
        self.assertIn("plan", event_types)
        self.assertIn("command_result", event_types)
        self.assertIn("evidence", event_types)
        self.assertIn("report_path", event_types)


if __name__ == "__main__":
    unittest.main()
