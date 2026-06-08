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

    def test_process_question_returns_local_analysis_without_api(self) -> None:
        result = self.methods.chat_message({"session_id": self.session["session_id"], "text": "哪个进程占 CPU"})

        self.assertEqual(result["intent"], "process_query")
        self.assertIn("结论：", result["message"])
        self.assertIn("关键证据：", result["message"])
        self.assertEqual(self.methods.sessions.get(self.session["session_id"]).latency_trace["api_call_count"], 0)

    def test_memory_usage_question_returns_local_analysis_without_api(self) -> None:
        result = self.methods.chat_message({"session_id": self.session["session_id"], "text": "查看内存占用"})

        self.assertEqual(result["intent"], "process_query")
        self.assertIn("结论：", result["message"])
        self.assertEqual(self.methods.sessions.get(self.session["session_id"]).latency_trace["api_call_count"], 0)


if __name__ == "__main__":
    unittest.main()
