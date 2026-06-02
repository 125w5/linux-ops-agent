import unittest

from diag.ai.doctor import doctor_provider, list_models


class ModelDoctorTests(unittest.TestCase):
    def test_model_list_contains_mock(self) -> None:
        self.assertIn("mock", list_models())

    def test_doctor_mentions_mock_demo_only(self) -> None:
        self.assertIn("mock", doctor_provider("mock"))
        self.assertIn("demo", doctor_provider("mock"))


if __name__ == "__main__":
    unittest.main()
