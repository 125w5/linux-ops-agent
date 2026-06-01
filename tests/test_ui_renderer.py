import json
import unittest

from diag.core.models import CommandResult, DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.ui.renderer import render_outcome


def sample_outcome() -> DiagnosisOutcome:
    plan = DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "Check df", "df -h", tool_name="disk.df")])
    outcome = DiagnosisOutcome.start("disk", plan)
    outcome.risk_level = "warning"
    outcome.root_causes = ["root cause"]
    outcome.suggestions = ["suggestion"]
    outcome.evidence = [EvidenceItem("df", "usage", "/ is 93%", "warning")]
    outcome.results = [CommandResult("df -h", "localhost", "raw output", "", 0, 1, "safe_readonly")]
    outcome.markdown_path = "report.md"
    return outcome


class UIRendererTests(unittest.TestCase):
    def test_compact_does_not_show_raw_output(self) -> None:
        rendered = render_outcome(sample_outcome(), view="compact")
        self.assertIn("Risk", rendered)
        self.assertNotIn("Raw command output", rendered)

    def test_json_style_is_parseable(self) -> None:
        rendered = render_outcome(sample_outcome(), style="json")
        data = json.loads(rendered)
        self.assertEqual(data["risk"], "warning")

    def test_quiet_is_machine_readable(self) -> None:
        rendered = render_outcome(sample_outcome(), view="quiet")
        data = json.loads(rendered)
        self.assertEqual(data["report_path"], "report.md")

    def test_verbose_shows_tools_but_not_raw_output(self) -> None:
        rendered = render_outcome(sample_outcome(), view="verbose")
        self.assertIn("Tool Calls", rendered)
        self.assertIn("disk.df", rendered)
        self.assertNotIn("raw output", rendered)

    def test_raw_shows_raw_output(self) -> None:
        rendered = render_outcome(sample_outcome(), view="raw")
        self.assertIn("Raw command output", rendered)
        self.assertIn("raw output", rendered)


if __name__ == "__main__":
    unittest.main()
