import unittest

from diag.engine.resource_schema import resource_event_payload, validate_resource_event


class ResourceSchemaTests(unittest.TestCase):
    def test_resource_schema_contains_required_fields(self) -> None:
        payload = resource_event_payload(
            {
                "sampler_status": "ready",
                "psutil_available": True,
                "logical_cpu_count": 8,
                "system": {"cpu_percent": 12, "memory_total_bytes": 1000, "memory_bytes": 400, "memory_percent": 40},
                "disk": {"mountpoint": "D:", "total_bytes": 2000, "used_bytes": 1000, "percent": 50},
                "top_cpu_processes": [{"pid": 1, "name": "edge", "raw_cpu_percent": 655, "memory_bytes": 5}],
                "top_memory_processes": [],
            }
        )
        self.assertEqual(validate_resource_event(payload), [])
        self.assertEqual(payload["top_cpu"][0]["normalized_cpu_percent"], 81.875)
        self.assertEqual(payload["top_cpu"][0]["raw_cpu_percent"], 655)

    def test_missing_fields_are_reported(self) -> None:
        errors = validate_resource_event({"event": "ResourceUpdated"})
        self.assertIn("missing memory", errors)


if __name__ == "__main__":
    unittest.main()
