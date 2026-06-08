import unittest

from diag.dashboard.resource_sampler import _error_sample


class TelemetryDegradedFallbackTests(unittest.TestCase):
    def test_missing_psutil_with_fallback_data_is_degraded(self) -> None:
        sample = _error_sample(ModuleNotFoundError("No module named 'psutil'"))
        self.assertIn(sample["sampler_status"], {"degraded", "error"})
        self.assertEqual(sample["sampler_error"], "psutil missing")


if __name__ == "__main__":
    unittest.main()
