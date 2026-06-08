import unittest

from diag.engine.resource_analysis import analyze_process_rows, analyze_resource_snapshot


class ResourceAnalysisTests(unittest.TestCase):
    def test_snapshot_analysis_turns_metrics_into_decision(self) -> None:
        result = analyze_resource_snapshot(
            {
                "sampler_status": "ready",
                "system_cpu_percent": 72,
                "memory": {"used_bytes": 10 * 1024**3, "total_bytes": 32 * 1024**3, "percent": 32},
                "disk": {"mount": "D:", "used_bytes": 323 * 1024**3, "total_bytes": 431 * 1024**3, "percent": 75},
                "top_cpu": [{"pid": 14684, "name": "Codex", "normalized_cpu_percent": 35.2, "raw_cpu_percent": 423, "memory_bytes": 480 * 1024**2}],
                "top_memory": [{"pid": 14808, "name": "chrome", "normalized_cpu_percent": 2, "raw_cpu_percent": 24, "memory_bytes": 542 * 1024**2}],
            },
            focus="overview",
        )

        self.assertIn("结论：", result["text"])
        self.assertIn("关键证据：", result["text"])
        self.assertIn("下一步：", result["text"])
        self.assertEqual(result["risk"], "warning")
        self.assertTrue(result["actions"])

    def test_process_analysis_preserves_raw_and_normalized_cpu(self) -> None:
        result = analyze_process_rows(
            [{"pid": 14684, "name": "Codex", "normalized_cpu_percent": 35.2, "raw_cpu_percent": 423, "memory_bytes": 480 * 1024**2}],
            focus="cpu",
            snapshot={"sampler_status": "ready"},
        )

        self.assertIn("35.2% system / 423% raw", result["text"])
        self.assertEqual(result["risk"], "info")
        self.assertTrue(any(action["command"] == "/process inspect 14684" for action in result["actions"]))


if __name__ == "__main__":
    unittest.main()
