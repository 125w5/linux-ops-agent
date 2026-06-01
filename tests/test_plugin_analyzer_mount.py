import unittest

from diag.plugins.loader import PluginLoader


class PluginAnalyzerMountTests(unittest.TestCase):
    def test_nginx_doctor_registers_analyzer(self) -> None:
        record = PluginLoader().doctor("nginx_ops")
        self.assertIsNotNone(record)
        self.assertIn("nginx.error_hint", record.analyzers or {})


if __name__ == "__main__":
    unittest.main()
