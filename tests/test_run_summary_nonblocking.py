import unittest

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep
from diag.engine.summary_builder import build_run_summary


class RunSummaryNonblockingTests(unittest.TestCase):
    def test_summary_is_available_without_report_path(self) -> None:
        outcome = DiagnosisOutcome.start("disk full", DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "df", "df -h")]))
        outcome.root_causes = ["disk usage needs review"]
        outcome.suggestions = ["inspect evidence first"]
        outcome.risk_level = "info"

        summary = build_run_summary(outcome)

        self.assertIn("诊断完成", str(summary["text"]))
        self.assertIn("报告：还没有写入完成", str(summary["text"]))


if __name__ == "__main__":
    unittest.main()
