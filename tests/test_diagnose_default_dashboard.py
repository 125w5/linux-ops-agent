import argparse
import unittest
from unittest.mock import patch

from diag.cli.app import _resolve_diagnose_view
from diag.ui.capabilities import TerminalCapabilities


class DiagnoseDefaultDashboardTests(unittest.TestCase):
    def test_default_tty_uses_plain_batch_mode(self) -> None:
        args = argparse.Namespace(view=None)
        caps = TerminalCapabilities(is_tty=True, width=120, color=True, ci=False, recommended_view="verbose")
        with patch("diag.cli.app.detect_capabilities", return_value=caps):
            self.assertEqual(_resolve_diagnose_view(args), "plain")

    def test_default_non_tty_uses_plain(self) -> None:
        args = argparse.Namespace(view=None)
        caps = TerminalCapabilities(is_tty=False, width=120, color=False, ci=False, recommended_view="normal")
        with patch("diag.cli.app.detect_capabilities", return_value=caps):
            self.assertEqual(_resolve_diagnose_view(args), "plain")


if __name__ == "__main__":
    unittest.main()
