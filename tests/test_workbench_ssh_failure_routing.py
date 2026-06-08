import unittest

from diag.workbench.app import build_workbench
from diag.workbench.command_router import WorkbenchCommandRouter
from diag.workbench.context import WorkbenchOptions


class WorkbenchSshFailureRoutingTests(unittest.TestCase):
    def test_plain_ssh_failure_input_generates_ssh_plan(self) -> None:
        loop = build_workbench(WorkbenchOptions(mode="demo"), output_func=lambda _text: None)
        router = WorkbenchCommandRouter(loop.state, loop.controller)

        response = router.handle("ssh failure")

        self.assertIn("Plan generated", response)
        self.assertIsNotNone(loop.state.current_plan)
        self.assertEqual(loop.state.task_type, "ssh-failure")
        commands = [step.command for step in loop.state.current_plan.steps]
        self.assertTrue(any("Failed password" in command or "auth.log" in command for command in commands))
        self.assertNotIn("df -h", commands)


if __name__ == "__main__":
    unittest.main()
