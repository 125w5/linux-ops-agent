import unittest

from diag.engine.fast_router import should_call_api_for_input


class NoApiForUiCommandsTests(unittest.TestCase):
    def test_ui_and_action_commands_do_not_need_api(self) -> None:
        commands = ["/help", "/config api", "/model list", "/resources", "/raw", "/report", "/approve", "/deny", "/tools", "/agents", "/usage"]
        for command in commands:
            self.assertFalse(should_call_api_for_input(command), command)


if __name__ == "__main__":
    unittest.main()
