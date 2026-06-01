import unittest

from diag.workbench.app import build_workbench
from diag.workbench.command_router import WorkbenchCommandRouter
from diag.workbench.context import WorkbenchOptions


class WorkbenchCommandRouterTests(unittest.TestCase):
    def test_plain_input_generates_plan_without_running(self) -> None:
        loop = build_workbench(WorkbenchOptions(mode="demo"), output_func=lambda _text: None)
        router = WorkbenchCommandRouter(loop.state, loop.controller)

        response = router.handle("检查磁盘")

        self.assertIn("Plan generated", response)
        self.assertIsNotNone(loop.state.current_plan)
        self.assertFalse(loop.state.running)

    def test_prefix_lists_commands(self) -> None:
        loop = build_workbench(WorkbenchOptions(mode="demo"), output_func=lambda _text: None)
        router = WorkbenchCommandRouter(loop.state, loop.controller)

        response = router.handle("/r")

        self.assertIn("/run", response)
        self.assertIn("/raw", response)
        self.assertIn("/report", response)
        self.assertIn("/resources", response)

    def test_explain_message_replies_without_plan(self) -> None:
        loop = build_workbench(WorkbenchOptions(mode="demo"), output_func=lambda _text: None)
        router = WorkbenchCommandRouter(loop.state, loop.controller)

        response = router.handle("为什么要检查磁盘？")

        self.assertIn("只读诊断", response)
        self.assertIsNone(loop.state.current_plan)

    def test_config_api_is_discoverable(self) -> None:
        loop = build_workbench(WorkbenchOptions(mode="demo"), output_func=lambda _text: None)
        router = WorkbenchCommandRouter(loop.state, loop.controller)

        response = router.handle("/config api")

        self.assertIn("API 配置入口", response)
        self.assertIn("/model doctor", response)


if __name__ == "__main__":
    unittest.main()
