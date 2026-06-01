import unittest

from diag.tui.widgets.command_palette import filter_commands, palette_commands, plugin_command, skill_command


class CommandPaletteTests(unittest.TestCase):
    def test_core_commands_include_run_and_config(self) -> None:
        names = [command.name for command in palette_commands()]
        self.assertIn("/run", names)
        self.assertIn("/config", names)

    def test_filter_commands(self) -> None:
        matches = filter_commands("resource")
        self.assertTrue(any(command.name == "/resources" for command in matches))

    def test_plugin_and_skill_commands_keep_source(self) -> None:
        commands = palette_commands([plugin_command("/nginx", "Nginx helper"), skill_command("/disk-skill", "Disk skill")])
        sources = {command.name: command.source for command in commands}
        self.assertEqual(sources["/nginx"], "plugin")
        self.assertEqual(sources["/disk-skill"], "skill")


if __name__ == "__main__":
    unittest.main()
