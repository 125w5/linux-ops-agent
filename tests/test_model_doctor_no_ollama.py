import unittest

from diag.ai.doctor import doctor_provider, list_models


class ModelDoctorNoOllamaTests(unittest.TestCase):
    def test_model_list_does_not_show_local_providers(self) -> None:
        text = list_models().lower()

        for blocked in ["ollama", "vllm", "llama_cpp", "offline"]:
            self.assertNotIn(blocked, text)

    def test_doctor_default_does_not_check_ollama(self) -> None:
        text = doctor_provider().lower()

        self.assertNotIn("ollama:", text)
        self.assertIn("missing_env", text)

    def test_doctor_reports_blocked_for_removed_provider(self) -> None:
        self.assertIn("blocked_local_ai", doctor_provider("ollama"))


if __name__ == "__main__":
    unittest.main()
