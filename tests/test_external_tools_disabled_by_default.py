import unittest

from diag.external_tools.manifest import ExternalToolManifest
from diag.external_tools.stdio_client import ExternalToolClient


class ExternalToolsDisabledByDefaultTests(unittest.TestCase):
    def test_enabled_external_tool_manifest_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ExternalToolManifest("demo", "demo-tool", enabled=True).validate()

    def test_non_readonly_external_tool_manifest_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ExternalToolManifest("demo", "demo-tool", permission="write").validate()

    def test_client_returns_disabled_response(self) -> None:
        response = ExternalToolClient(ExternalToolManifest("demo", "demo-tool")).call({})
        self.assertFalse(response["ok"])


if __name__ == "__main__":
    unittest.main()
