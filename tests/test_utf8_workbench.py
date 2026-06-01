import json
import tempfile
import unittest
from pathlib import Path

from diag.workbench.message import WorkbenchMessage
from diag.workbench.session import WorkbenchSession


class Utf8WorkbenchTests(unittest.TestCase):
    def test_workbench_transcript_keeps_chinese_unescaped(self) -> None:
        session = WorkbenchSession("session-utf8")
        session.append_message(WorkbenchMessage("user", "检查磁盘"))

        with tempfile.TemporaryDirectory() as tmp:
            path = session.write(Path(tmp))
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)

        self.assertEqual(data["events"][0]["payload"]["content"], "检查磁盘")
        self.assertIn("检查磁盘", content)
        self.assertNotIn("\\u68", content)


if __name__ == "__main__":
    unittest.main()
