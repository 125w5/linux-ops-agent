import unittest

from diag.engine.fast_router import route_fast_path, should_call_api_for_input


class KnownOpsTasksToolFirstTests(unittest.TestCase):
    def test_known_ops_tasks_are_fast(self) -> None:
        for text in ["disk full", "cpu high", "memory leak", "nginx failed", "docker status", "systemd service", "ssh failure", "journal logs", "mysql status"]:
            self.assertTrue(route_fast_path(text).fast, text)
            self.assertFalse(should_call_api_for_input(text), text)


if __name__ == "__main__":
    unittest.main()
