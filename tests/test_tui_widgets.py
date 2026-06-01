import unittest

from diag.tui.state import TuiState
from diag.tui.widgets import audit_pane, command_input, evidence_pane, model_pane, plan_pane, plugin_pane, raw_pane, report_pane, resources_pane, status_bar, transcript_pane


class TuiWidgetsTests(unittest.TestCase):
    def test_widgets_render_from_state(self) -> None:
        state = TuiState()
        self.assertIn("StatusBar", status_bar.render(state))
        self.assertIn("CommandInput", command_input.render(state))
        self.assertIn("PlanPane", plan_pane.render(state))
        self.assertIn("EvidencePane", evidence_pane.render(state))
        self.assertIn("RawPane", raw_pane.render(state))
        self.assertIn("ReportPane", report_pane.render(state))
        self.assertIn("ResourcesPane", resources_pane.render(state))
        self.assertIn("PluginPane", plugin_pane.render(state))
        self.assertIn("ModelPane", model_pane.render(state))
        self.assertIn("TranscriptPane", transcript_pane.render(state))
        self.assertIn("AuditPane", audit_pane.render(state))


if __name__ == "__main__":
    unittest.main()
