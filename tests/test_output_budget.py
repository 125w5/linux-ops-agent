import unittest

from diag.core.models import CommandResult
from diag.resources.budget import ResourceBudget
from diag.resources.limiter import apply_output_limits
from diag.resources.output_budget import truncate_text
from diag.resources.usage import ResourceUsage


class OutputBudgetTests(unittest.TestCase):
    def test_truncate_text_marks_truncated(self) -> None:
        text, truncated = truncate_text("abcdef", 3)
        self.assertTrue(truncated)
        self.assertIn("truncated", text)

    def test_apply_output_limits_sets_result_flag(self) -> None:
        result = CommandResult("x", "localhost", "abcdef", "", 0, 1, "safe_readonly")
        usage = ResourceUsage()
        apply_output_limits(result, ResourceBudget(max_stdout_bytes_per_command=3), usage)
        self.assertTrue(result.truncated)
        self.assertEqual(usage.truncated_results, 1)


if __name__ == "__main__":
    unittest.main()
