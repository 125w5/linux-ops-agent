import unittest

from diag.engine.smoke import run_engine_smoke


class EngineSmokeTests(unittest.TestCase):
    def test_engine_smoke_passes(self) -> None:
        ok, text = run_engine_smoke()
        self.assertTrue(ok, text)
        self.assertIn("engine smoke ok", text)


if __name__ == "__main__":
    unittest.main()
