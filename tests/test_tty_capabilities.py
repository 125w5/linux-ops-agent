import unittest

from diag.ui.capabilities import detect_capabilities


class TTYCapabilitiesTests(unittest.TestCase):
    def test_narrow_tty_recommends_compact(self) -> None:
        caps = detect_capabilities(width=60, is_tty=True)
        self.assertEqual(caps.recommended_view, "compact")

    def test_wide_tty_recommends_verbose(self) -> None:
        caps = detect_capabilities(width=140, is_tty=True)
        self.assertEqual(caps.recommended_view, "verbose")


if __name__ == "__main__":
    unittest.main()
