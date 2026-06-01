import io
import tempfile
import unittest
from pathlib import Path

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class ApiConfigRpcTests(unittest.TestCase):
    def test_api_config_flow_saves_env_name_not_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            local_path = Path(directory) / "local.yaml"
            methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
            methods._local_path = lambda: local_path  # type: ignore[method-assign]
            session = methods.session_start({"mode": "demo"})

            methods.config_api_start({"session_id": session["session_id"], "provider": "deepseek"})
            methods.config_api_set_api_key_env({"session_id": session["session_id"], "api_key_env": "DEEPSEEK_API_KEY"})
            preview = methods.config_api_preview({"session_id": session["session_id"]})
            saved = methods.config_api_save({"session_id": session["session_id"]})

            content = local_path.read_text(encoding="utf-8")
            self.assertIn("DEEPSEEK_API_KEY", preview["yaml"])
            self.assertIn("DEEPSEEK_API_KEY", content)
            self.assertNotIn("sk-", content)
            self.assertEqual(saved["provider"], "deepseek")

    def test_real_api_key_is_rejected(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        session = methods.session_start({"mode": "demo"})
        methods.config_api_start({"session_id": session["session_id"], "provider": "openai"})

        with self.assertRaises(ValueError):
            methods.config_api_set_api_key_env({"session_id": session["session_id"], "api_key_env": "sk-real-secret"})


if __name__ == "__main__":
    unittest.main()
