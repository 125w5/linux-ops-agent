import unittest

from diag.agents.registry import list_agents


class SubagentInheritsSandboxTests(unittest.TestCase):
    def test_listed_agents_inherit_current_sandbox_profile(self) -> None:
        agents = list_agents("ops-read")

        self.assertTrue(agents)
        self.assertTrue(all(agent["sandbox_profile"] == "ops-read" for agent in agents))
        self.assertIn("LogAgent", {agent["name"] for agent in agents})


if __name__ == "__main__":
    unittest.main()
