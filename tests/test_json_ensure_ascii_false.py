import tempfile
import unittest
from pathlib import Path

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.reports.json_report import write_json_report


class JsonEnsureAsciiFalseTests(unittest.TestCase):
    def test_json_report_keeps_chinese_unescaped(self) -> None:
        plan = DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "Check disk", "df -h")])
        outcome = DiagnosisOutcome.start("检查磁盘", plan)
        outcome.evidence = [EvidenceItem("df", "usage", "根目录使用率 93%", "warning")]

        with tempfile.TemporaryDirectory() as tmp:
            path = write_json_report(outcome, Path(tmp))
            content = path.read_text(encoding="utf-8")

        self.assertIn("检查磁盘", content)
        self.assertIn("根目录使用率", content)
        self.assertNotIn("\\u68", content)


if __name__ == "__main__":
    unittest.main()
