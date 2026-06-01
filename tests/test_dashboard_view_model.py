import unittest

from diag.dashboard.view_model import DashboardViewModel


class DashboardViewModelTests(unittest.TestCase):
    def test_view_model_tracks_runtime_events(self) -> None:
        vm = DashboardViewModel()
        vm.apply("SessionStarted", {"session_id": "session-1", "target": "localhost", "task_type": "disk", "mode": "readonly"})
        vm.apply(
            "PlanCreated",
            {
                "task_type": "disk",
                "target": "localhost",
                "steps": [{"id": "df", "name": "Check disk", "command": "df -h", "risk": "safe_readonly", "tool_name": "disk.df"}],
            },
        )
        vm.apply("ToolStarted", {"step_id": "df", "command": "df -h", "tool_name": "disk.df"})
        vm.apply("ToolFinished", {"step_id": "df", "command": "df -h", "status": 0, "stdout_bytes": 42})
        vm.apply("EvidenceAdded", {"items": [{"severity": "warning", "content": "根目录使用率 93%"}]})
        vm.apply("ReportWritten", {"markdown_path": "report.md", "json_path": "report.json"})

        self.assertEqual(vm.session_id, "session-1")
        self.assertEqual(vm.tool_calls[0].status, "done")
        self.assertIn("df -h -> done", vm.raw_summary)
        self.assertEqual(vm.evidence[0]["content"], "根目录使用率 93%")
        self.assertEqual(vm.report_path, "report.md")


if __name__ == "__main__":
    unittest.main()
