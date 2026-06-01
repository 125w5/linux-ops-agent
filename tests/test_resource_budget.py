import unittest

from diag.resources.budget import load_resource_budget
from diag.resources.command_budget import command_allowed


class ResourceBudgetTests(unittest.TestCase):
    def test_default_budget_values(self) -> None:
        budget = load_resource_budget()
        self.assertEqual(budget.command_timeout_seconds, 15)
        self.assertFalse(budget.ai.allow_cloud_in_demo)

    def test_command_budget_blocks_after_limit(self) -> None:
        budget = load_resource_budget()
        self.assertTrue(command_allowed(0, budget))
        self.assertFalse(command_allowed(budget.max_commands_per_session, budget))


if __name__ == "__main__":
    unittest.main()
