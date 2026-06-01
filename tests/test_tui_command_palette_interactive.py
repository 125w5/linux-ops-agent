import unittest

from diag.tui.widgets.command_palette import CommandPaletteState, palette_commands, render_palette


class TuiCommandPaletteInteractiveTests(unittest.TestCase):
    def test_palette_filters_and_executes_selection(self) -> None:
        state = CommandPaletteState(palette_commands(), open=True)
        state.input("res")
        self.assertEqual(state.execute_selected(), "/resources")
        self.assertIn("/resources", render_palette(state))

    def test_palette_backspace(self) -> None:
        state = CommandPaletteState(palette_commands(), query="run")
        state.backspace()
        self.assertEqual(state.query, "ru")


if __name__ == "__main__":
    unittest.main()
