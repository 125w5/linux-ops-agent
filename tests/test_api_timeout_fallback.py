import time
import unittest

from diag.engine.fast_router import call_with_timeout_fallback


class ApiTimeoutFallbackTests(unittest.TestCase):
    def test_api_timeout_returns_fallback_without_waiting_for_slow_call(self) -> None:
        started = time.perf_counter()

        result = call_with_timeout_fallback(lambda: time.sleep(1.0), timeout_seconds=0.05, fallback_result={"plan": "rule"})

        self.assertTrue(result.fallback)
        self.assertEqual(result.reason, "api_timeout")
        self.assertEqual(result.result, {"plan": "rule"})
        self.assertLess(time.perf_counter() - started, 0.5)


if __name__ == "__main__":
    unittest.main()
