import unittest

from diag.tui.actions import TuiAction
from diag.tui.keymap import action_for_key, textual_bindings


class TuiKeymapTests(unittest.TestCase):
    def test_action_for_key(self) -> None:
        self.assertEqual(action_for_key("F5"), TuiAction.RUN)

    def test_textual_bindings_shape(self) -> None:
        self.assertTrue(any(row[0] == "F1" for row in textual_bindings()))


if __name__ == "__main__":
    unittest.main()
