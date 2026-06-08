import unittest

from diag.engine.fast_router import route_fast_path, should_use_remote_planner


class FastRouterNoLlmTests(unittest.TestCase):
    def test_common_commands_are_fast_path(self) -> None:
        for text in ["/help", "/config api", "/model doctor", "/resources", "/raw", "/report"]:
            self.assertTrue(route_fast_path(text).fast, text)

    def test_greeting_and_api_config_are_fast_path(self) -> None:
        self.assertTrue(route_fast_path("你好").fast)
        self.assertTrue(route_fast_path("配置 API").fast)

    def test_fault_description_is_tool_first(self) -> None:
        self.assertTrue(route_fast_path("nginx 服务 502 故障，请诊断").fast)
        self.assertFalse(should_use_remote_planner("nginx 服务 502 故障，请诊断"))


if __name__ == "__main__":
    unittest.main()
