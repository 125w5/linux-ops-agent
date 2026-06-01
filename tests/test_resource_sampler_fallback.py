import unittest
from unittest.mock import patch

from diag.dashboard.resource_sampler import sample_resources


class ResourceSamplerFallbackTests(unittest.TestCase):
    def test_fallback_returns_resource_shape_when_psutil_fails(self) -> None:
        with patch("diag.dashboard.resource_sampler._sample_psutil", side_effect=RuntimeError("missing")):
            snapshot = sample_resources()

        self.assertIn("system", snapshot)
        self.assertIn("disk", snapshot)
        self.assertIn("top_cpu_processes", snapshot)
        self.assertIn("top_memory_processes", snapshot)


if __name__ == "__main__":
    unittest.main()
