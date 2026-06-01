import contextlib
import io
import unittest

from diag.cli.app import build_parser


class SessionAttachTests(unittest.TestCase):
    def test_task_attach_command_exists(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["task", "attach", "--last"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            args.func(args)
        self.assertTrue("Attached session summary" in output.getvalue() or "No task found" in output.getvalue())


if __name__ == "__main__":
    unittest.main()
