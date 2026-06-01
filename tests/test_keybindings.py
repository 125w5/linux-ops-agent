import unittest

from diag.tui.bindings import load_keybindings


class KeybindingTests(unittest.TestCase):
    def test_core_binding_present(self) -> None:
        bindings = load_keybindings()
        self.assertEqual(bindings.bindings["F5"], "run")

    def test_plugin_cannot_override_core_shortcut(self) -> None:
        bindings = load_keybindings({"F5": "plugin_run"})
        self.assertEqual(bindings.bindings["F5"], "run")
        self.assertIn("F5", bindings.conflicts)


if __name__ == "__main__":
    unittest.main()
