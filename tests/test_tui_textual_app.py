import unittest

from diag.tui.app import build_textual_app_class


class TuiTextualAppTests(unittest.TestCase):
    def test_textual_app_factory_is_optional(self) -> None:
        app_class = build_textual_app_class()
        self.assertTrue(app_class is None or hasattr(app_class, "run"))


if __name__ == "__main__":
    unittest.main()
