import unittest

from diag.workbench.app import run_workbench
from diag.workbench.context import WorkbenchOptions


class WorkbenchLoopTests(unittest.TestCase):
    def test_exit_is_required_to_leave_loop(self) -> None:
        inputs = iter(["检查磁盘", "/exit"])
        output: list[str] = []

        code = run_workbench(
            WorkbenchOptions(target="localhost", mode="demo", task="disk"),
            input_func=lambda _prompt: next(inputs),
            output_func=output.append,
        )

        self.assertEqual(code, 0)
        self.assertTrue(any("diag>" not in line for line in output))
        self.assertTrue(any("Plan generated" in line for line in output))
        self.assertTrue(any("Workbench transcript:" in line for line in output))


if __name__ == "__main__":
    unittest.main()
