import unittest

from diag.tui.controller import TuiController
from diag.tui.state import TuiState


class TuiControllerTests(unittest.TestCase):
    def test_plan_updates_state_via_bridge(self) -> None:
        state = TuiState()
        controller = TuiController(state)
        controller.plan("disk")
        self.assertGreater(len(state.plan), 0)

    def test_raw_toggle(self) -> None:
        controller = TuiController(TuiState())
        self.assertTrue(controller.toggle_raw())
        self.assertFalse(controller.toggle_raw())


if __name__ == "__main__":
    unittest.main()
