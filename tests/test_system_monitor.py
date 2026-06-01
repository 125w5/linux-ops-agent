import unittest

from diag.dashboard.system_monitor import SystemMonitor


class SystemMonitorTests(unittest.TestCase):
    def test_sample_once_never_raises_and_updates_snapshot(self) -> None:
        seen = []
        monitor = SystemMonitor(on_sample=seen.append)
        snapshot = monitor.sample_once()

        self.assertIsInstance(snapshot, dict)
        self.assertEqual(monitor.last_snapshot, snapshot)
        self.assertEqual(seen[-1], snapshot)


if __name__ == "__main__":
    unittest.main()
