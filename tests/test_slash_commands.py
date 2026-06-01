import unittest

from diag.interactive.command_parser import parse_interactive_input
from diag.interactive.session_state import InteractiveSessionState
from diag.interactive.slash_commands import handle_slash_command, plan_from_text
from diag.permissions.mode import PermissionMode


class SlashCommandTests(unittest.TestCase):
    def test_natural_language_generates_plan_only(self) -> None:
        state = InteractiveSessionState("localhost", PermissionMode.DEMO)
        message = plan_from_text(state, "disk is full")
        self.assertIn("Plan generated", message)
        self.assertIsNotNone(state.plan)
        self.assertIsNone(state.outcome)

    def test_parse_slash_command(self) -> None:
        parsed = parse_interactive_input("/plan disk")
        self.assertTrue(parsed.is_command)
        self.assertEqual(parsed.name, "/plan")
        self.assertEqual(parsed.args, "disk")

    def test_status_command(self) -> None:
        state = InteractiveSessionState("localhost", PermissionMode.DEMO)
        _, output = handle_slash_command(state, "/status", "", lambda _state: None)
        self.assertIn("target=localhost", output)


if __name__ == "__main__":
    unittest.main()
