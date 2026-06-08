import unittest
from unittest import mock

from diag.dashboard.resource_sampler import ProcessSampler


class TelemetryErrorWhenPsutilMissingTests(unittest.TestCase):
    def test_psutil_missing_is_degraded_when_fallback_has_data(self) -> None:
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "psutil":
                raise ModuleNotFoundError("No module named 'psutil'")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=fake_import):
            sample = ProcessSampler().sample()
        self.assertIn(sample["sampler_status"], {"degraded", "error"})
        self.assertEqual(sample["sampler_error"], "psutil missing")
        if sample["sampler_status"] == "degraded":
            self.assertTrue(sample["fallback_active"])


if __name__ == "__main__":
    unittest.main()
