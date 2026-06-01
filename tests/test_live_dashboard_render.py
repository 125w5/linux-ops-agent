import unittest

from diag.dashboard.renderers import render_plain_dashboard
from diag.dashboard.view_model import DashboardViewModel


class LiveDashboardRenderTests(unittest.TestCase):
    def test_plain_dashboard_contains_required_sections_and_folded_raw(self) -> None:
        vm = DashboardViewModel(session_id="abcdef123", task="disk", target="localhost", mode="readonly")
        vm.apply_resources(
            {
                "system": {"cpu_percent": 12.5, "memory_used_gb": 2.0, "memory_total_gb": 8.0, "memory_percent": 25.0},
                "disk": {"mountpoint": "/", "used_gb": 20.0, "total_gb": 40.0, "percent": 50.0},
            }
        )
        vm.raw_summary.append("df -h -> done")

        output = render_plain_dashboard(vm)

        self.assertIn("OpsPilot-Linux", output)
        self.assertIn("Plan / Tool Calls", output)
        self.assertIn("Evidence", output)
        self.assertIn("Resources", output)
        self.assertIn("Raw Summary", output)
        self.assertIn("folded", output)
        self.assertIn("Commands:", output)


if __name__ == "__main__":
    unittest.main()
