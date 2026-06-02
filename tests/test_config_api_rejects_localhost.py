import unittest

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class ConfigApiRejectsLocalhostTests(unittest.TestCase):
    def test_config_api_rejects_localhost_base_url(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})
        methods.config_api_start({"session_id": session["session_id"], "provider": "custom"})

        with self.assertRaisesRegex(ValueError, "本地 AI 已禁用|远程 API"):
            methods.config_api_set_base_url({"session_id": session["session_id"], "base_url": "http://localhost:11434"})

    def test_config_api_rejects_local_model_words(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})
        methods.config_api_start({"session_id": session["session_id"], "provider": "custom"})

        with self.assertRaisesRegex(ValueError, "禁用本地 AI"):
            methods.config_api_set_model({"session_id": session["session_id"], "model": "ollama/llama3"})


if __name__ == "__main__":
    unittest.main()
