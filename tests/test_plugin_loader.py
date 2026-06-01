import unittest

from diag.plugins.loader import PluginLoader


class PluginLoaderTests(unittest.TestCase):
    def test_discover_lists_default_disabled_plugins(self) -> None:
        registry = PluginLoader().discover()
        nginx = registry.get("nginx_ops")
        self.assertIsNotNone(nginx)
        self.assertFalse(nginx.enabled)
        self.assertTrue(nginx.valid)

    def test_doctor_validates_plugin_entry_tools(self) -> None:
        record = PluginLoader().doctor("nginx_ops")
        self.assertIsNotNone(record)
        self.assertTrue(record.valid)


if __name__ == "__main__":
    unittest.main()
