import unittest

from diag.safety.command_checker import check_command


class SafetyTests(unittest.TestCase):
    def test_allows_readonly_pipeline(self) -> None:
        decision = check_command("du -h --max-depth=1 / 2>/dev/null | sort -hr | head")
        self.assertTrue(decision.allowed)

    def test_blocks_dangerous_command(self) -> None:
        decision = check_command("rm -rf /var/log/*")
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
