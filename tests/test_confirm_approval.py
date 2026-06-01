import unittest

from diag.core.models import RiskLevel
from diag.permissions.approval import StaticApprovalProvider
from diag.permissions.mode import PermissionMode
from diag.permissions.policy import PermissionPolicy


class ConfirmApprovalTests(unittest.TestCase):
    def test_low_risk_confirm_can_approve(self) -> None:
        policy = PermissionPolicy(PermissionMode.CONFIRM, StaticApprovalProvider(True))
        decision = policy.evaluate("df -h", preset_risk=RiskLevel.LOW_RISK)
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.requires_confirmation)

    def test_low_risk_confirm_can_deny(self) -> None:
        policy = PermissionPolicy(PermissionMode.CONFIRM, StaticApprovalProvider(False))
        decision = policy.evaluate("df -h", preset_risk=RiskLevel.LOW_RISK)
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_confirmation)


if __name__ == "__main__":
    unittest.main()
