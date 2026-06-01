import unittest

from diag.workbench.panes.monitor_pane import render_monitor_pane
from diag.workbench.state import WorkbenchState


class WorkbenchMonitorLiveTests(unittest.TestCase):
    def test_monitor_pane_shows_resource_snapshot(self) -> None:
        state = WorkbenchState()
        state.set_resources(
            {
                "system": {"cpu_percent": 10.0, "memory_used_gb": 1.0, "memory_total_gb": 4.0, "memory_percent": 25.0},
                "disk": {"mountpoint": "/", "used_gb": 2.0, "total_gb": 8.0, "percent": 25.0},
            }
        )

        output = render_monitor_pane(state)

        self.assertIn("MonitorPane", output)
        self.assertIn("CPU 10.0%", output)
        self.assertIn("Mem 1.0/4.0GB 25.0%", output)


if __name__ == "__main__":
    unittest.main()
