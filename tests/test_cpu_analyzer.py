import unittest

from diag.analyzers.cpu_analyzer import analyze_cpu
from diag.core.models import CommandResult


def result(command: str, stdout: str) -> CommandResult:
    return CommandResult(command, "localhost", stdout, "", 0, 1, "safe_readonly")


class CpuAnalyzerTests(unittest.TestCase):
    def test_detects_high_load_and_top_process(self) -> None:
        evidence, causes, suggestions, risk = analyze_cpu(
            [
                result("uptime", "load average: 5.82, 4.31, 3.22"),
                result("ps aux --sort=-%cpu | head", "USER PID %CPU COMMAND\napp 1 99.9 python\n"),
            ]
        )
        self.assertEqual(risk, "critical")
        self.assertTrue(any(item.evidence_type == "load_average" for item in evidence))
        self.assertTrue(causes)
        self.assertTrue(suggestions)


if __name__ == "__main__":
    unittest.main()
