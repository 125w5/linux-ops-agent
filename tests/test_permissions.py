import unittest

from diag.permissions.mode import PermissionMode, parse_permission_mode
from diag.permissions.policy import PermissionPolicy


class PermissionTests(unittest.TestCase):
    def test_demo_flag_selects_demo_mode(self) -> None:
        self.assertEqual(parse_permission_mode(None, demo=True), PermissionMode.DEMO)

    def test_readonly_allows_readonly_command(self) -> None:
        decision = PermissionPolicy(PermissionMode.READONLY).evaluate("df -h")
        self.assertTrue(decision.allowed)

    def test_dangerous_command_is_blocked(self) -> None:
        decision = PermissionPolicy(PermissionMode.READONLY).evaluate("rm -rf /tmp/x")
        self.assertFalse(decision.allowed)

    def test_blocked_mode_blocks_even_readonly(self) -> None:
        decision = PermissionPolicy(PermissionMode.BLOCKED).evaluate("df -h")
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
