import unittest

from diag.workbench.state import WorkbenchState


class WorkbenchRealtimeEventsTests(unittest.TestCase):
    def test_runtime_events_update_state_immediately(self) -> None:
        state = WorkbenchState()
        state.apply_event("ToolStarted", {"step_id": "df", "command": "df -h", "tool_name": "disk.df"})
        self.assertEqual(state.dashboard.tool_calls[0].status, "running")

        state.apply_event("ToolFinished", {"step_id": "df", "command": "df -h", "tool_name": "disk.df", "status": 0})
        self.assertEqual(state.dashboard.tool_calls[0].status, "done")

        state.apply_event("EvidenceAdded", {"items": [{"severity": "warning", "content": "根目录使用率 93%"}]})
        self.assertEqual(state.dashboard.evidence[0]["content"], "根目录使用率 93%")


if __name__ == "__main__":
    unittest.main()
