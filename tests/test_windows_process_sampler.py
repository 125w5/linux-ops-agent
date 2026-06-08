import unittest

from diag.dashboard.resource_sampler import ProcessSampler


class WindowsProcessSamplerTests(unittest.TestCase):
    def test_sampler_reports_status_instead_of_silent_na(self) -> None:
        sample = ProcessSampler().sample()
        self.assertIn(sample["sampler_status"], {"warming_up", "error"})
        if sample["sampler_status"] == "error":
            self.assertTrue(sample.get("sampler_error"))


if __name__ == "__main__":
    unittest.main()
