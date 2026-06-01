import unittest

from diag.plugins.manifest import PluginManifest
from diag.plugins.registry import PluginRecord, PluginRegistry


class PluginRegistryTests(unittest.TestCase):
    def test_add_and_get_record(self) -> None:
        registry = PluginRegistry()
        manifest = PluginManifest("x", "0.1", "desc", "entry.py")
        registry.add(PluginRecord(manifest, enabled=False, valid=True, errors=[]))
        self.assertEqual(registry.get("x").manifest.name, "x")  # type: ignore[union-attr]


if __name__ == "__main__":
    unittest.main()
