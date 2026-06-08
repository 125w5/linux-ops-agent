import unittest

from diag.permissions.approval import StaticApprovalProvider
from diag.permissions.mode import PermissionMode
from diag.permissions.policy import PermissionPolicy
from diag.permissions.sandbox_profiles import list_sandbox_profiles


class SandboxProfilesTests(unittest.TestCase):
    def test_profiles_are_listed(self) -> None:
        names = {profile["name"] for profile in list_sandbox_profiles()}
        self.assertEqual({"safe-read", "ops-read", "lab-write", "admin-confirm"}, names)

    def test_safe_read_blocks_low_risk_validation(self) -> None:
        decision = PermissionPolicy(PermissionMode.READONLY, sandbox_profile="safe-read").evaluate("nginx -t")
        self.assertFalse(decision.allowed)

    def test_ops_read_allows_validation_and_systemd_cat(self) -> None:
        policy = PermissionPolicy(PermissionMode.READONLY, sandbox_profile="ops-read")
        self.assertTrue(policy.evaluate("nginx -t").allowed)
        self.assertTrue(policy.evaluate("systemctl cat nginx").allowed)

    def test_admin_confirm_asks_without_auto_execution(self) -> None:
        policy = PermissionPolicy(PermissionMode.CONFIRM, StaticApprovalProvider(False), sandbox_profile="admin-confirm")
        decision = policy.evaluate("nginx -t")
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_confirmation)

    def test_dangerous_commands_remain_blocked(self) -> None:
        decision = PermissionPolicy(PermissionMode.CONFIRM, StaticApprovalProvider(True), sandbox_profile="admin-confirm").evaluate("rm -rf /")
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
