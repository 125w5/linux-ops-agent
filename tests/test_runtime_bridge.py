import unittest

from diag.tui.runtime_bridge import RuntimeEventBridge


class RuntimeBridgeTests(unittest.TestCase):
    def test_bridge_updates_state_from_events(self) -> None:
        bridge = RuntimeEventBridge()
        bridge.emit("SessionStarted", {"session_id": "s1"})
        bridge.emit("PlanCreated", {"steps": [{"id": "df"}]})
        bridge.emit("ToolFinished", {"command": "df -h", "status": 0})
        bridge.emit("ResourceUpdated", {"tui_render_ms": 1})
        self.assertEqual(bridge.state.session_id, "s1")
        self.assertEqual(len(bridge.state.plan), 1)
        self.assertIn("df -h", bridge.state.raw[0])
        self.assertEqual(bridge.state.resources["tui_render_ms"], 1)
        self.assertTrue(bridge.state.audit)


if __name__ == "__main__":
    unittest.main()
