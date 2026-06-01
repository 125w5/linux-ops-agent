import json
import tempfile
import unittest
from pathlib import Path

from diag.core.models import DiagnosisOutcome, DiagnosisPlan, DiagnosisStep, EvidenceItem
from diag.reports.markdown_report import write_markdown_report


class Utf8OutputTests(unittest.TestCase):
    def test_markdown_report_writes_chinese_as_utf8(self) -> None:
        plan = DiagnosisPlan("disk", "localhost", [DiagnosisStep("df", "Check disk", "df -h")])
        outcome = DiagnosisOutcome.start("检查磁盘", plan)
        outcome.evidence = [EvidenceItem("df", "usage", "根目录使用率 93%", "warning")]
        outcome.root_causes = ["日志文件过大"]
        outcome.suggestions = ["清理旧日志"]

        with tempfile.TemporaryDirectory() as tmp:
            path = write_markdown_report(outcome, Path(tmp))
            content = path.read_text(encoding="utf-8")

        self.assertIn("检查磁盘", content)
        self.assertIn("根目录使用率", content)
        self.assertNotIn("\\u6839", content)


if __name__ == "__main__":
    unittest.main()
