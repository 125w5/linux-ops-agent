import unittest

from diag.tui.widgets.approval_modal import ApprovalModal


class ApprovalModalTests(unittest.TestCase):
    def test_low_risk_modal_allows_approve_or_deny(self) -> None:
        text = ApprovalModal("df -h", "low_risk", "confirm").render()
        self.assertIn("/approve", text)
        self.assertIn("/deny", text)

    def test_blocked_modal_cannot_approve(self) -> None:
        text = ApprovalModal("rm -rf /", "blocked", "danger").render()
        self.assertIn("Approval is not available", text)


if __name__ == "__main__":
    unittest.main()
