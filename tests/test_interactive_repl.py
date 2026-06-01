import unittest

from diag.interactive.repl import run_interactive_repl
from diag.interactive.session_state import InteractiveSessionState
from diag.permissions.mode import PermissionMode


class InteractiveReplTests(unittest.TestCase):
    def test_repl_help_and_exit(self) -> None:
        inputs = iter(["/help", "/exit"])
        outputs: list[str] = []
        state = InteractiveSessionState("localhost", PermissionMode.DEMO)
        code = run_interactive_repl(state, input_func=lambda _prompt: next(inputs), output_func=outputs.append)
        self.assertEqual(code, 0)
        self.assertTrue(any("/run" in output for output in outputs))


if __name__ == "__main__":
    unittest.main()
