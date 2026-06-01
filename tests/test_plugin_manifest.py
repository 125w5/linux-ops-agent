import unittest
from pathlib import Path

from diag.plugins.manifest import PluginManifest
from diag.plugins.validator import validate_manifest


class PluginManifestTests(unittest.TestCase):
    def test_manifest_loads_nginx_plugin(self) -> None:
        manifest = PluginManifest.from_file(Path("plugins/nginx_ops/plugin.yaml"))
        self.assertEqual(manifest.name, "nginx_ops")
        self.assertFalse(validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
