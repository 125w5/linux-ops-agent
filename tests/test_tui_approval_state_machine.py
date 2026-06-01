import unittest

from diag.tui.controller import TuiController
from diag.tui.state import TuiState


class TuiApprovalStateMachineTests(unittest.TestCase):
    def test_approve_resolves_pending_command(self) -> None:
        controller = TuiController(TuiState())
        pending = controller.request_approval("df -h", "low_risk", "confirm")
        self.assertFalse(pending.resolved)
        self.assertTrue(controller.approve())
        self.assertTrue(pending.resolved)
        self.assertTrue(pending.approved)

    def test_blocked_command_cannot_be_approved(self) -> None:
        controller = TuiController(TuiState())
        controller.request_approval("rm -rf /", "blocked", "danger")
        self.assertFalse(controller.approve())


if __name__ == "__main__":
    unittest.main()
