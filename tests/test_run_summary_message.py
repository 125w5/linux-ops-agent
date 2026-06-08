import unittest

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.engine.summary_builder import build_run_summary


class RunSummaryMessageTests(unittest.TestCase):
    def test_run_summary_contains_conclusion_evidence_risk_and_actions(self) -> None:
        plan = DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "disk usage", "df -h")])
        outcome = DiagnosisOutcome.start("check disk", plan)
        outcome.evidence = [EvidenceItem("journalctl", "journal_usage", "journal logs about 1GB", "warning")]
        outcome.root_causes = ["/var/log is consuming significant space"]
        outcome.suggestions = ["Review journal retention before deleting anything"]
        outcome.risk_level = "warning"
        outcome.markdown_path = "reports/demo.md"

        summary = build_run_summary(outcome)

        self.assertIn("诊断完成", str(summary["text"]))
        self.assertIn("你问的是：check disk", str(summary["text"]))
        self.assertIn("journal logs about 1GB", str(summary["text"]))
        self.assertIn("风险：warning", str(summary["text"]))
        self.assertTrue(summary["actions"])


if __name__ == "__main__":
    unittest.main()
