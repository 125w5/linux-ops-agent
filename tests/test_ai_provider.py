import unittest

from diag.ai.providers.mock_provider import MockProvider
from diag.ai.providers.openai_provider import OpenAIProvider
from diag.ai.message import LLMMessage


class AIProviderTests(unittest.TestCase):
    def test_mock_provider_complete_and_healthcheck(self) -> None:
        provider = MockProvider()
        response = provider.complete([LLMMessage("user", "planner")])
        self.assertEqual(response.provider, "mock")
        self.assertTrue(provider.healthcheck().ok)

    def test_cloud_provider_missing_key_is_friendly(self) -> None:
        provider = OpenAIProvider(api_key_env="OPSPILOT_TEST_MISSING_KEY")
        health = provider.healthcheck()
        self.assertFalse(health.ok)
        self.assertIn("Missing API key env var", health.message)


if __name__ == "__main__":
    unittest.main()
