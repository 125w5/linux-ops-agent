import io
import json
import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineSshFailureRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.output = io.StringIO()
        self.methods = EngineMethods(EngineSessionManager(), EventStream(lambda line: self.output.write(line + "\n")))
        self.session = self.methods.session_start({"target": "localhost", "mode": "demo", "task": "disk"})

    def events(self) -> list[dict]:
        return [json.loads(line) for line in self.output.getvalue().splitlines() if line.strip()]

    def test_plan_create_does_not_let_default_disk_override_ssh_input(self) -> None:
        plan = self.methods.plan_create({"session_id": self.session["session_id"], "input": "ssh failure"})

        self.assertEqual(plan["task_type"], "ssh-failure")
        self.assertEqual(self.methods.sessions.get(self.session["session_id"]).task, "ssh-failure")
        commands = [step["command"] for step in plan["steps"]]
        self.assertTrue(any("Failed password" in command or "auth.log" in command for command in commands))
        self.assertNotIn("df -h", commands)

    def test_chat_message_routes_chinese_ssh_failure_to_ssh_plan(self) -> None:
        result = self.methods.chat_message({"session_id": self.session["session_id"], "text": "ssh\u5931\u8d25\u68c0\u6d4b"})

        self.assertIn("plan", result)
        self.assertEqual(result["plan"]["task_type"], "ssh-failure")
        plan_events = [event for event in self.events() if event.get("event") == "PlanCreated"]
        self.assertEqual(plan_events[-1]["payload"]["task_type"], "ssh-failure")


if __name__ == "__main__":
    unittest.main()
