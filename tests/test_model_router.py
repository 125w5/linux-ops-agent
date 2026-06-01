import unittest

from diag.ai.model_router import ModelRouter


class ModelRouterTests(unittest.TestCase):
    def test_force_mock_planner_returns_structured_result(self) -> None:
        router = ModelRouter(force_mock=True)
        result = router.planner("disk full", ["disk.df"])
        self.assertEqual(result["provider"], "mock")
        self.assertIn("tool_calls", result["result"])


if __name__ == "__main__":
    unittest.main()
