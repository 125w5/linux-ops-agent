import unittest

from diag.ai.config import resolve_provider_config


class ModelApiFirstTests(unittest.TestCase):
    def test_default_profile_prefers_api_provider(self) -> None:
        config = resolve_provider_config()

        self.assertNotEqual(config.type, "ollama")
        self.assertIn(config.type, {"openai", "anthropic", "openai-compatible"})

    def test_ollama_is_explicit_offline_profile(self) -> None:
        config = resolve_provider_config(profile="offline")

        self.assertEqual(config.type, "ollama")


if __name__ == "__main__":
    unittest.main()
