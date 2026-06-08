import unittest

from diag.safety.command_checker import check_command
from diag.tools.registry import build_default_registry


class ProcessToolsPermissionsTests(unittest.TestCase):
    def test_process_tools_are_registered_with_expected_risks(self) -> None:
        registry = build_default_registry()

        self.assertEqual(registry.get("process.list_top_cpu").risk.value, "safe_readonly")
        self.assertEqual(registry.get("process.inspect").risk.value, "safe_readonly")
        self.assertEqual(registry.get("process.tree").risk.value, "safe_readonly")
        self.assertEqual(registry.get("process.kill_term").risk.value, "low_risk")
        self.assertEqual(registry.get("process.kill_kill").risk.value, "blocked")

    def test_process_tree_is_safe_read_and_sigkill_is_blocked(self) -> None:
        self.assertTrue(check_command("pstree -ap 123").allowed)
        sigkill = check_command("kill -9 123")
        self.assertFalse(sigkill.allowed)
        self.assertEqual(sigkill.risk_level.value, "blocked")


if __name__ == "__main__":
    unittest.main()
