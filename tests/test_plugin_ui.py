import unittest
from pathlib import Path
import contextlib
import io

from diag.cli.app import build_parser
from diag.plugins.manifest import PluginManifest


class PluginUITests(unittest.TestCase):
    def test_manifest_ui_metadata(self) -> None:
        manifest = PluginManifest.from_file(Path("plugins/nginx_ops/plugin.yaml"))
        self.assertEqual(manifest.ui["category"], "service")
        self.assertEqual(manifest.ui["display_name"], "Nginx Ops")

    def test_plugin_doctor_uses_visual_checks(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["plugin", "doctor", "nginx_ops"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        self.assertEqual(code, 0)
        self.assertIn("Plugin Doctor", output.getvalue())
        self.assertIn("[PASS]", output.getvalue())


if __name__ == "__main__":
    unittest.main()
