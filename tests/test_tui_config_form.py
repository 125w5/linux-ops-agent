import unittest

from diag.tui.widgets.config_screen import preview_local_yaml_update


class TuiConfigFormTests(unittest.TestCase):
    def test_config_form_preview_mentions_next_effect(self) -> None:
        diff = preview_local_yaml_update("tui", "default_layout", "wide")
        self.assertIn("default_layout", diff.after)


if __name__ == "__main__":
    unittest.main()
