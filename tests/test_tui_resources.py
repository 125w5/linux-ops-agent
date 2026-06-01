import unittest

from diag.tui.app import choose_layout, render_workbench_snapshot
from diag.tui.pagination import preview_bytes, tail_lines
from diag.tui.panes import render_raw_pane
from diag.tui.state import TuiState


class TuiResourcesTests(unittest.TestCase):
    def test_snapshot_shows_tui_render_metric(self) -> None:
        state = TuiState(layout="default")
        state.resources["tui_render_ms"] = 12
        self.assertIn("tui_render_ms=12", render_workbench_snapshot(state))

    def test_requested_layout_wins(self) -> None:
        self.assertEqual(choose_layout("debug"), "debug")

    def test_raw_pane_limits_to_last_200_lines(self) -> None:
        state = TuiState(layout="debug")
        state.raw = [f"line {index}" for index in range(250)]
        rendered = render_raw_pane(state, expanded=True)
        self.assertIn("[truncated]", rendered)
        self.assertNotIn("line 0", rendered)
        self.assertIn("line 249", rendered)

    def test_report_preview_truncates_to_budget(self) -> None:
        page = preview_bytes("x" * (101 * 1024), 100 * 1024)
        self.assertTrue(page.truncated)

    def test_tail_lines_helper(self) -> None:
        page = tail_lines([str(index) for index in range(205)], 200)
        self.assertTrue(page.truncated)


if __name__ == "__main__":
    unittest.main()
