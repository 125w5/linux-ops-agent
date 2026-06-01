import unittest
from unittest.mock import patch

from diag.dashboard import resource_sampler


class ResourceEventVisualFieldsTests(unittest.TestCase):
    def test_windows_mountpoint_is_displayed_as_drive(self) -> None:
        with patch.object(resource_sampler.os, "name", "nt"):
            self.assertEqual(resource_sampler._display_mountpoint("D:\\"), "D:")


if __name__ == "__main__":
    unittest.main()
