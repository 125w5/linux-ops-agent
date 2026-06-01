import unittest

from diag.resources.token_budget import estimate_tokens, fit_text_to_token_budget, within_token_budget


class TokenBudgetTests(unittest.TestCase):
    def test_estimate_and_check(self) -> None:
        self.assertGreater(estimate_tokens("abcd"), 0)
        self.assertFalse(within_token_budget("x" * 100, 1))

    def test_fit_text_truncates_when_needed(self) -> None:
        text, truncated = fit_text_to_token_budget("x" * 100, 5)
        self.assertTrue(truncated)
        self.assertIn("AI input budget exceeded", text)


if __name__ == "__main__":
    unittest.main()
