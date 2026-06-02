import unittest

from diag.ai.config import resolve_provider_config
from diag.ai.model_router import build_provider
from diag.utils.config_loader import load_config


class NoLocalAiProviderTests(unittest.TestCase):
    def test_config_provider_list_has_no_local_ai(self) -> None:
        providers = load_config().get("providers", {})
        names = ",".join(providers.keys()).lower()

        for blocked in ["ollama", "vllm", "llama_cpp", "offline"]:
            self.assertNotIn(blocked, names)

    def test_no_callable_ollama_provider(self) -> None:
        with self.assertRaises(ValueError):
            resolve_provider_config(provider="ollama")

    def test_local_provider_type_is_not_built(self) -> None:
        with self.assertRaises(Exception):
            build_provider(type("Config", (), {"type": "ollama", "model": "llama3", "name": "ollama"})())


if __name__ == "__main__":
    unittest.main()
