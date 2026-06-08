import unittest

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.engine.summary_builder import build_report_summary


class ReportSummaryChineseTests(unittest.TestCase):
    def test_report_summary_answers_user_question_in_chinese(self) -> None:
        outcome = DiagnosisOutcome.start("查看内存占用", DiagnosisPlan("memory", "localhost", [DiagnosisStep("mem", "memory", "free -h")]))
        outcome.evidence = [EvidenceItem("ps", "top_memory", "chrome uses 542MB", "info")]
        outcome.root_causes = ["没有发现明显内存压力"]
        outcome.suggestions = ["继续观察 Top MEM 进程"]
        outcome.risk_level = "info"
        outcome.markdown_path = "outputs/reports/demo.md"

        summary = build_report_summary(outcome)

        self.assertIn("报告已生成", str(summary["text"]))
        self.assertIn("你问的是：查看内存占用", str(summary["text"]))
        self.assertIn("回答：我检查了内存占用", str(summary["text"]))
        self.assertIn("chrome uses 542MB", str(summary["text"]))


if __name__ == "__main__":
    unittest.main()
