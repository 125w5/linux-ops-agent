import unittest

from diag.executor.ssh_executor import SSHExecutor, load_ssh_host


class SSHExecutorTests(unittest.TestCase):
    def test_hosts_config_loads(self) -> None:
        host = load_ssh_host("node-01")
        self.assertIsNotNone(host)
        self.assertEqual(host.port, 22)

    def test_demo_mode_blocks_real_ssh(self) -> None:
        result = SSHExecutor(demo=True).run("df -h", "node-01", "safe_readonly")
        self.assertTrue(result.skipped)
        self.assertIn("disabled in demo mode", result.stderr)


if __name__ == "__main__":
    unittest.main()
