import unittest

from diag.analyzers.service_analyzer import analyze_service
from diag.core.models import CommandResult


def result(command: str, stdout: str) -> CommandResult:
    return CommandResult(command, "localhost", stdout, "", 0, 1, "safe_readonly")


class ServiceAnalyzerTests(unittest.TestCase):
    def test_detects_failed_port_conflict_and_config_error(self) -> None:
        evidence, causes, suggestions, risk = analyze_service(
            [
                result("systemctl status nginx", "Active: failed (Result: exit-code)"),
                result("journalctl -u nginx -n 50", "bind() to 0.0.0.0:80 failed (98: Address already in use)\nconfiguration file /etc/nginx/nginx.conf test failed"),
                result("ss -tulnp", "tcp LISTEN 0 511 0.0.0.0:80 0.0.0.0:* users:((\"apache2\",pid=1))"),
            ],
            service="nginx",
        )
        self.assertEqual(risk, "critical")
        self.assertTrue(any(item.evidence_type == "port_conflict" for item in evidence))
        self.assertTrue(any("port conflict" in cause.lower() for cause in causes))
        self.assertTrue(suggestions)


if __name__ == "__main__":
    unittest.main()
