import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class ApiConfigRejectsLocalAiTests(unittest.TestCase):
    def test_localhost_base_url_is_rejected(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})
        methods.config_api_start({"session_id": session["session_id"], "provider": "openai"})

        with self.assertRaises(ValueError):
            methods.config_api_set_base_url({"session_id": session["session_id"], "base_url": "http://127.0.0.1:11434/v1"})

    def test_local_model_name_is_rejected(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})
        methods.config_api_start({"session_id": session["session_id"], "provider": "openai"})

        with self.assertRaises(ValueError):
            methods.config_api_set_model({"session_id": session["session_id"], "model": "local model"})


if __name__ == "__main__":
    unittest.main()
