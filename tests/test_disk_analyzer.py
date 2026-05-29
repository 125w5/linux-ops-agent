import unittest

from diag.analyzers.disk_analyzer import analyze_disk
from diag.core.models import CommandResult


def result(command: str, stdout: str) -> CommandResult:
    return CommandResult(command, "localhost", stdout, "", 0, 1, "safe_readonly")


class DiskAnalyzerTests(unittest.TestCase):
    def test_disk_analyzer_detects_log_and_docker_usage(self) -> None:
        evidence, causes, suggestions, risk = analyze_disk(
            [
                result("df -h", "Filesystem Size Used Avail Use% Mounted on\n/dev/sda1 40G 37G 3G 93% /\n"),
                result(
                    "du -h --max-depth=1 / 2>/dev/null | sort -hr | head",
                    "18G /var\n12G /var/lib/docker\n9G /var/log\n",
                ),
                result("find / -type f -size +500M 2>/dev/null | head", "/var/log/app.log\n"),
            ]
        )

        self.assertEqual(risk, "warning")
        self.assertTrue(any(item.evidence_type == "filesystem_usage" for item in evidence))
        self.assertTrue(any("Docker" in cause for cause in causes))
        self.assertTrue(any("logrotate" in suggestion for suggestion in suggestions))


if __name__ == "__main__":
    unittest.main()
