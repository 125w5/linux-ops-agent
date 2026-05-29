import unittest

from diag.tools.registry import build_default_registry


class ToolRegistryTests(unittest.TestCase):
    def test_registry_contains_disk_and_service_tools(self) -> None:
        registry = build_default_registry()
        disk_tools = registry.for_scene("disk")
        service_tools = registry.for_scene("service")
        self.assertTrue(any(tool.name == "disk.df" for tool in disk_tools))
        self.assertTrue(any(tool.name == "service.status" for tool in service_tools))
        self.assertIn("{service}", registry.get("service.status").command_template)


if __name__ == "__main__":
    unittest.main()
