import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class ActionCardsRpcTests(unittest.TestCase):
    def test_assistant_replies_carry_action_cards(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})

        result = methods.chat_message({"session_id": session["session_id"], "text": "help me configure api"})

        self.assertTrue(result["actions"])
        self.assertTrue(any(action["command"] == "/config api" for action in result["actions"]))


if __name__ == "__main__":
    unittest.main()
