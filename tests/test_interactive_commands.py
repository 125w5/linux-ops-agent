import contextlib
import io
import unittest

from diag.cli.app import build_parser


class InteractiveCommandsTests(unittest.TestCase):
    def test_statusline_preview_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["statusline", "preview"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("session=", output.getvalue())

    def test_health_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["health"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("provider", output.getvalue())


if __name__ == "__main__":
    unittest.main()
