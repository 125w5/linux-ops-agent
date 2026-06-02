import unittest

from diag.ai.config import LOCAL_AI_DISABLED_CONFIG_MESSAGE
from diag.ai.config import resolve_provider_config


class ModelApiFirstTests(unittest.TestCase):
    def test_default_profile_prefers_api_provider(self) -> None:
        config = resolve_provider_config()

        self.assertNotEqual(config.type, "ollama")
        self.assertIn(config.type, {"openai", "anthropic", "openai-compatible"})

    def test_offline_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, LOCAL_AI_DISABLED_CONFIG_MESSAGE):
            resolve_provider_config(profile="offline")


if __name__ == "__main__":
    unittest.main()
