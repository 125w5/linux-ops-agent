import unittest

from diag.tui.fallback import render_plain_fallback
from diag.tui.state import TuiState


class TuiFallbackTests(unittest.TestCase):
    def test_plain_fallback_mentions_existing_cli(self) -> None:
        text = render_plain_fallback(TuiState())
        self.assertIn("diag chat", text)
        self.assertIn("diag diagnose", text)


if __name__ == "__main__":
    unittest.main()
