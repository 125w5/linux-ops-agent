import unittest

from diag.tui.layouts import load_layout


class TuiLayoutsTests(unittest.TestCase):
    def test_wide_layout_contains_model_pane(self) -> None:
        layout = load_layout("wide")
        self.assertIn("ModelPane", layout.panes)

    def test_debug_layout_contains_raw_pane(self) -> None:
        layout = load_layout("debug")
        self.assertIn("RawPane", layout.panes)


if __name__ == "__main__":
    unittest.main()
