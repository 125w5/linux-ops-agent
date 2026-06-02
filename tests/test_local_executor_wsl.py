import subprocess
import unittest
from unittest.mock import patch

from diag.executor.local_executor import LocalExecutor


class LocalExecutorWslTests(unittest.TestCase):
    def test_windows_uses_wsl_for_linux_commands(self) -> None:
        completed = subprocess.CompletedProcess(["wsl.exe"], 0, stdout=b"ok\n", stderr=b"")
        with patch("platform.system", return_value="Windows"), patch("shutil.which", return_value="C:/Windows/System32/wsl.exe"), patch(
            "subprocess.run", return_value=completed
        ) as run:
            result = LocalExecutor().run("df -h", "localhost", "safe_readonly")

        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, "ok\n")
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["wsl.exe", "bash", "-lc", "df -h"])

    def test_windows_without_wsl_reports_setup_hint(self) -> None:
        with patch("platform.system", return_value="Windows"), patch("shutil.which", return_value=None):
            result = LocalExecutor().run("df -h", "localhost", "safe_readonly")

        self.assertEqual(result.return_code, 127)
        self.assertIn("wsl --install -d Ubuntu", result.stderr)

    def test_windows_wsl_pending_reboot_reports_restart_hint(self) -> None:
        completed = subprocess.CompletedProcess(["wsl.exe"], 1, stdout=b"", stderr=b"Wsl/WSL_E_WSL_OPTIONAL_COMPONENT_REQUIRED")
        with patch("platform.system", return_value="Windows"), patch("shutil.which", return_value="C:/Windows/System32/wsl.exe"), patch(
            "subprocess.run", return_value=completed
        ):
            result = LocalExecutor().run("df -h", "localhost", "safe_readonly")

        self.assertEqual(result.return_code, 1)
        self.assertIn("Restart Windows", result.stderr)


if __name__ == "__main__":
    unittest.main()
