import contextlib
import io
import unittest

from diag.cli.app import build_parser


class TuiEntryTests(unittest.TestCase):
    def test_tui_command_falls_back_in_non_tty(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tui", "--target", "localhost", "--mode", "demo"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("TUI fallback", output.getvalue())


if __name__ == "__main__":
    unittest.main()
