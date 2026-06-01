import unittest

from diag.engine.chat_router import route_chat


class ChatRouterTests(unittest.TestCase):
    def test_greeting_does_not_route_to_fault_plan(self) -> None:
        self.assertEqual(route_chat("你好").intent, "greeting")

    def test_api_config_request_routes_to_api_flow(self) -> None:
        self.assertEqual(route_chat("你能帮我配置 API 吗").intent, "api_config")
        self.assertEqual(route_chat("帮我配置 deepseek").intent, "api_config")

    def test_fault_description_routes_to_plan(self) -> None:
        self.assertEqual(route_chat("服务器磁盘是不是有问题").intent, "fault_description")

    def test_proc_kcore_routes_to_evidence_question(self) -> None:
        self.assertEqual(route_chat("/proc/kcore 能删吗").intent, "evidence_question")


if __name__ == "__main__":
    unittest.main()
