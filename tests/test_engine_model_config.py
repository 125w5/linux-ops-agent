import io
import tempfile
import unittest
from pathlib import Path

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.session_manager import EngineSessionManager


class EngineModelConfigTests(unittest.TestCase):
    def test_model_set_writes_local_yaml_without_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            local_path = Path(directory) / "local.yaml"
            methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
            methods._local_path = lambda: local_path  # type: ignore[method-assign]

            result = methods.model_set({"model": "openai:gpt-4.1-mini"})

            content = local_path.read_text(encoding="utf-8")
            self.assertEqual(result["provider"], "openai")
            self.assertIn("default: openai", content)
            self.assertIn("model: gpt-4.1-mini", content)
            self.assertNotIn("api_key:", content)

    def test_model_list_reports_env_presence_not_secret_value(self) -> None:
        methods = EngineMethods(EngineSessionManager(), EventStream(lambda _line: None))
        result = methods.model_list({})

        self.assertIn("providers", result)
        self.assertIn("text", result)
        self.assertNotIn("sk-", str(result))


if __name__ == "__main__":
    unittest.main()
