import unittest
from unittest.mock import patch

from diag.ai.errors import NeedApiConfig
from diag.ai.model_router import ModelRouter


class ApiOnlyModelRouterTests(unittest.TestCase):
    def test_demo_mode_uses_mock(self) -> None:
        router = ModelRouter(force_mock=True)

        self.assertEqual(router.config.name, "mock")

    def test_normal_mode_without_api_key_needs_config(self) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            with self.assertRaises(NeedApiConfig):
                ModelRouter(provider="openai")

    def test_normal_mode_cannot_use_mock(self) -> None:
        with self.assertRaises(NeedApiConfig):
            ModelRouter(provider="mock")


if __name__ == "__main__":
    unittest.main()
