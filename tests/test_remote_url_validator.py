import unittest

from diag.ai.errors import LLMConfigurationError
from diag.ai.remote_url_validator import validate_remote_api_url


class RemoteUrlValidatorTests(unittest.TestCase):
    def test_blocks_local_urls(self) -> None:
        blocked = [
            "http://localhost:11434",
            "http://127.0.0.1:11434",
            "http://0.0.0.0:11434",
            "http://[::1]:11434",
            "file:///tmp/socket",
            "http+unix://%2Fvar%2Frun%2Fllm.sock",
            "unix:///var/run/llm.sock",
            "http://10.0.0.2/v1",
            "http://172.16.1.2/v1",
            "http://192.168.1.20/v1",
        ]

        for url in blocked:
            with self.subTest(url=url):
                with self.assertRaises(LLMConfigurationError):
                    validate_remote_api_url(url)

    def test_allows_remote_gateway_urls(self) -> None:
        self.assertEqual(validate_remote_api_url("https://relay.example.com/v1"), "https://relay.example.com/v1")
        self.assertEqual(validate_remote_api_url("https://api.openai.com/v1"), "https://api.openai.com/v1")


if __name__ == "__main__":
    unittest.main()
