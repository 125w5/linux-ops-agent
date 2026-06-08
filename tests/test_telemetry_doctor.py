import unittest

from diag.engine.telemetry_doctor import telemetry_doctor


class TelemetryDoctorTests(unittest.TestCase):
    def test_psutil_missing_is_visible(self) -> None:
        result = telemetry_doctor({"sampler_status": "error", "sampler_error": "psutil missing", "psutil_available": False})
        self.assertIn("psutil available: False", result["text"])
        self.assertIn("sampler error: psutil missing", result["text"])


if __name__ == "__main__":
    unittest.main()
