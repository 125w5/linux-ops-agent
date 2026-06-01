import threading
import time
import unittest

from diag.permissions.approval import ApprovalRequest
from diag.workbench.controller import WorkbenchApprovalProvider
from diag.workbench.state import WorkbenchState


class WorkbenchApprovalPauseResumeTests(unittest.TestCase):
    def test_approve_resumes_pending_request(self) -> None:
        state = WorkbenchState()
        provider = WorkbenchApprovalProvider(state)
        result = {}

        thread = threading.Thread(target=lambda: result.setdefault("decision", provider.request(ApprovalRequest("echo ok", "confirm"))))
        thread.start()
        time.sleep(0.1)
        self.assertTrue(state.approval.pending)

        with state.approval_condition:
            state.approval.decision = True
            state.approval_condition.notify_all()
        thread.join(timeout=2)

        self.assertTrue(result["decision"].approved)

    def test_deny_resumes_pending_request(self) -> None:
        state = WorkbenchState()
        provider = WorkbenchApprovalProvider(state)
        result = {}

        thread = threading.Thread(target=lambda: result.setdefault("decision", provider.request(ApprovalRequest("echo ok", "confirm"))))
        thread.start()
        time.sleep(0.1)
        with state.approval_condition:
            state.approval.decision = False
            state.approval_condition.notify_all()
        thread.join(timeout=2)

        self.assertFalse(result["decision"].approved)


if __name__ == "__main__":
    unittest.main()
