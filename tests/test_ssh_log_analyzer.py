import unittest

from diag.analyzers.ssh_log_analyzer import analyze_ssh_failures
from diag.core.models import CommandResult


def result(command: str, stdout: str) -> CommandResult:
    return CommandResult(command, "localhost", stdout, "", 0, 1, "safe_readonly")


class SshLogAnalyzerTests(unittest.TestCase):
    def test_counts_failed_passwords_ips_and_users(self) -> None:
        output = "\n".join(
            [
                "May 29 sshd[1]: Failed password for root from 203.0.113.8 port 1 ssh2",
                "May 29 sshd[2]: Failed password for invalid user admin from 203.0.113.8 port 2 ssh2",
                "May 29 sshd[3]: Failed password for test from 198.51.100.24 port 3 ssh2",
                "May 29 sshd[4]: Failed password for root from 203.0.113.8 port 4 ssh2",
                "May 29 sshd[5]: Failed password for root from 203.0.113.8 port 5 ssh2",
            ]
        )
        evidence, causes, suggestions, risk = analyze_ssh_failures(
            [result("grep 'Failed password' /var/log/auth.log | tail -100", output)]
        )
        self.assertEqual(risk, "warning")
        self.assertTrue(any(item.evidence_type == "source_ips" for item in evidence))
        self.assertTrue(causes)
        self.assertTrue(suggestions)


if __name__ == "__main__":
    unittest.main()
