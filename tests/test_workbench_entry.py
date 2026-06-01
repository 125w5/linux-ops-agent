import unittest

from diag.workbench.app import build_workbench
from diag.workbench.context import WorkbenchOptions


class WorkbenchEntryTests(unittest.TestCase):
    def test_build_workbench_uses_options(self) -> None:
        loop = build_workbench(WorkbenchOptions(target="localhost", mode="demo", task="disk"), output_func=lambda _text: None)

        self.assertEqual(loop.state.target, "localhost")
        self.assertEqual(loop.state.mode.value, "demo")
        self.assertEqual(loop.state.task_type, "disk")


if __name__ == "__main__":
    unittest.main()
