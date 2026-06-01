import unittest

from diag.tui.widgets.config_screen import preview_local_yaml_update, redact_provider_env_status, render_config_screen


class ConfigTuiTests(unittest.TestCase):
    def test_config_screen_redacts_env_values(self) -> None:
        text = render_config_screen()
        self.assertIn("Provider env", text)
        self.assertNotIn("sk-", text)

    def test_preview_local_yaml_update_has_diff_text(self) -> None:
        diff = preview_local_yaml_update("ui", "layout", "wide")
        self.assertIn("after", diff.render())
        self.assertIn("local.yaml", str(diff.path))
        self.assertIn("ui:", diff.after)

    def test_provider_status_uses_env_names_only(self) -> None:
        status = redact_provider_env_status()
        self.assertIn("openai", status)
        self.assertIn("OPENAI_API_KEY", status["openai"])


if __name__ == "__main__":
    unittest.main()
