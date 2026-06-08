import unittest

from diag.engine.fast_router import route_fast_path, should_call_api_for_input


class FastRouterLatencyTests(unittest.TestCase):
    def test_ui_commands_do_not_call_api(self) -> None:
        for text in ["/help", "/config api", "/model doctor", "/plugin", "/resources", "/raw", "/report", "/exit", "/permissions", "/tools", "/agents", "/usage"]:
            self.assertTrue(route_fast_path(text).fast, text)
            self.assertFalse(should_call_api_for_input(text), text)

    def test_greeting_does_not_call_api(self) -> None:
        self.assertTrue(route_fast_path("hello").fast)
        self.assertFalse(should_call_api_for_input("hello"))

    def test_known_ops_fault_does_not_wait_for_api(self) -> None:
        self.assertTrue(route_fast_path("nginx service cpu disk fault").fast)
        self.assertFalse(should_call_api_for_input("nginx service cpu disk fault"))


if __name__ == "__main__":
    unittest.main()
