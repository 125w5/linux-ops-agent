import unittest

from diag.core.models import RiskLevel
from diag.tools.registry import build_default_registry


class OpsReadToolsTests(unittest.TestCase):
    def test_ops_tool_expansion_is_registered(self) -> None:
        registry = build_default_registry()
        expected = {
            "nginx.config_test": RiskLevel.LOW_RISK,
            "docker.ps": RiskLevel.SAFE_READONLY,
            "docker.logs": RiskLevel.SAFE_READONLY,
            "systemd.failed_units": RiskLevel.SAFE_READONLY,
            "systemd.cat": RiskLevel.LOW_RISK,
            "network.listen": RiskLevel.SAFE_READONLY,
            "security.sudo_log": RiskLevel.SAFE_READONLY,
            "mysql.status": RiskLevel.SAFE_READONLY,
        }

        for name, risk in expected.items():
            self.assertEqual(registry.get(name).risk, risk)


if __name__ == "__main__":
    unittest.main()
