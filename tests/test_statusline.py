import unittest

from diag.ui.statusline import StatusLineData, render_statusline


class StatusLineTests(unittest.TestCase):
    def test_statusline_contains_key_fields(self) -> None:
        line = render_statusline(
            StatusLineData("abcdef123", "disk", "localhost", "demo", "mock", "m", 5, 10, 128, "warning")
        )
        self.assertIn("task=disk", line)
        self.assertIn("risk=warning", line)


if __name__ == "__main__":
    unittest.main()
