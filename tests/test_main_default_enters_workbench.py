import unittest
from unittest.mock import patch

from diag.cli import app


class MainDefaultEntersWorkbenchTests(unittest.TestCase):
    def test_no_args_defaults_to_workbench(self) -> None:
        with patch("diag.cli.app.run_workbench_command", return_value=0) as run_workbench:
            code = app.main([])

        self.assertEqual(code, 0)
        self.assertTrue(run_workbench.called)


if __name__ == "__main__":
    unittest.main()
