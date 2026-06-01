import contextlib
import io
import unittest

from diag.cli.app import build_parser


class PluginCliTests(unittest.TestCase):
    def test_plugin_list_cli(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["plugin", "list"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("nginx_ops", output.getvalue())

    def test_plugin_doctor_cli(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["plugin", "doctor", "nginx_ops"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("OK", output.getvalue())


if __name__ == "__main__":
    unittest.main()
