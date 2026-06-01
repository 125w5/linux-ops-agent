import argparse
import unittest
from unittest.mock import patch

from diag.cli.app import _resolve_diagnose_view
from diag.ui.capabilities import TerminalCapabilities


class DashboardNonTtyFallbackTests(unittest.TestCase):
    def test_ci_defaults_to_plain(self) -> None:
        args = argparse.Namespace(view=None)
        caps = TerminalCapabilities(is_tty=True, width=120, color=True, ci=True, recommended_view="quiet")
        with patch("diag.cli.app.detect_capabilities", return_value=caps):
            self.assertEqual(_resolve_diagnose_view(args), "plain")

    def test_explicit_dashboard_is_preserved_for_snapshot_rendering(self) -> None:
        args = argparse.Namespace(view="dashboard")
        caps = TerminalCapabilities(is_tty=False, width=120, color=False, ci=False, recommended_view="normal")
        with patch("diag.cli.app.detect_capabilities", return_value=caps):
            self.assertEqual(_resolve_diagnose_view(args), "dashboard")


if __name__ == "__main__":
    unittest.main()
