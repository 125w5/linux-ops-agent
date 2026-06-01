import unittest

from diag.tui.scroll import ScrollState


class TuiScrollTests(unittest.TestCase):
    def test_scroll_page_up_down(self) -> None:
        scroll = ScrollState()
        self.assertEqual(scroll.page_down("RawPane", page_size=20), 20)
        self.assertEqual(scroll.page_up("RawPane", page_size=10), 10)


if __name__ == "__main__":
    unittest.main()
