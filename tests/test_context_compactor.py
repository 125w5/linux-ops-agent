import unittest

from diag.engine.context_compactor import compact_messages


class ContextCompactorTests(unittest.TestCase):
    def test_keeps_recent_messages_and_summarizes_old_context(self) -> None:
        messages = [{"role": "user", "content": f"m{i}"} for i in range(12)]
        result = compact_messages(messages, keep_last=4)

        self.assertTrue(result["compacted"])
        self.assertEqual(len(result["messages"]), 5)
        self.assertEqual(result["messages"][0]["role"], "system")
        self.assertEqual(result["messages"][-1]["content"], "m11")


if __name__ == "__main__":
    unittest.main()
