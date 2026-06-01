import unittest

from diag.engine.prompt_pack import PROMPT_NAMES, load_prompt_pack


class PromptPackLoadingTests(unittest.TestCase):
    def test_prompt_pack_contains_expected_roles(self) -> None:
        pack = load_prompt_pack()

        self.assertEqual(set(pack), set(PROMPT_NAMES))
        self.assertIn("never", pack["system"].lower())
        self.assertIn("api_key_env", pack["api_config_assistant"])


if __name__ == "__main__":
    unittest.main()
