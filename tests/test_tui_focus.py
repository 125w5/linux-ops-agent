import unittest

from diag.tui.focus import FocusRing


class TuiFocusTests(unittest.TestCase):
    def test_focus_moves_forward_and_backward(self) -> None:
        focus = FocusRing(["PlanPane", "EvidencePane"])
        self.assertEqual(focus.active, "PlanPane")
        self.assertEqual(focus.next(), "EvidencePane")
        self.assertEqual(focus.previous(), "PlanPane")


if __name__ == "__main__":
    unittest.main()
