import json
import tempfile
import unittest
from pathlib import Path

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.reports.markdown_report import write_markdown_report


class ReportStyleFileTests(unittest.TestCase):
    def test_student_report_style_applies_to_file(self) -> None:
        outcome = DiagnosisOutcome.start("disk", DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "Check df", "df -h")]))
        outcome.evidence = [EvidenceItem("df", "usage", "/ is 93%", "warning")]
        with tempfile.TemporaryDirectory() as tmp:
            path = write_markdown_report(outcome, Path(tmp), style="student")
            self.assertIn("Student Diagnosis", path.read_text(encoding="utf-8"))

    def test_json_report_style_is_parseable(self) -> None:
        outcome = DiagnosisOutcome.start("disk", DiagnosisPlan("disk", "localhost", []))
        with tempfile.TemporaryDirectory() as tmp:
            path = write_markdown_report(outcome, Path(tmp), style="json")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["task_type"], "disk")


if __name__ == "__main__":
    unittest.main()
