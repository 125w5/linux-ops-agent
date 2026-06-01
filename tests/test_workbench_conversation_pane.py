import unittest

from diag.workbench.panes.conversation_pane import render_conversation_pane
from diag.workbench.state import WorkbenchState


class WorkbenchConversationPaneTests(unittest.TestCase):
    def test_conversation_pane_shows_user_and_agent_messages(self) -> None:
        state = WorkbenchState()
        state.add_message("user", "检查磁盘")
        state.add_message("agent", "Plan generated")

        output = render_conversation_pane(state)

        self.assertIn("ConversationPane", output)
        self.assertIn("user: 检查磁盘", output)
        self.assertIn("agent: Plan generated", output)


if __name__ == "__main__":
    unittest.main()
