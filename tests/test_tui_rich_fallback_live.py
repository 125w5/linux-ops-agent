import unittest

from diag.tui.fallback import run_rich_live_snapshot


class TuiRichFallbackLiveTests(unittest.TestCase):
    def test_live_snapshot_callable_runs(self) -> None:
        run_rich_live_snapshot(lambda: "snapshot", iterations=1)


if __name__ == "__main__":
    unittest.main()
