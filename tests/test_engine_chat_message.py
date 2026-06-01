import io
import json
import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineChatMessageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.output = io.StringIO()
        self.methods = EngineMethods(EngineSessionManager(), EventStream(lambda line: self.output.write(line + "\n")))
        self.session = self.methods.session_start({"target": "localhost", "mode": "demo", "task": "disk"})

    def events(self) -> list[dict]:
        return [json.loads(line) for line in self.output.getvalue().splitlines() if line.strip()]

    def test_explain_is_conversational_without_plan(self) -> None:
        result = self.methods.chat_message({"session_id": self.session["session_id"], "text": "为什么要检查磁盘？"})

        self.assertEqual(result["intent"], "evidence_question")
        self.assertIn("当前会话还没有证据", result["message"])
        self.assertNotIn("PlanCreated", [event.get("event") for event in self.events()])

    def test_plain_message_creates_plan(self) -> None:
        result = self.methods.chat_message({"session_id": self.session["session_id"], "text": "检查磁盘"})

        self.assertEqual(result["intent"], "fault_description")
        self.assertIn("plan", result)
        self.assertIn("PlanCreated", [event.get("event") for event in self.events()])


if __name__ == "__main__":
    unittest.main()
