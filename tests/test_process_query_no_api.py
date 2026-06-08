import unittest

from diag.engine.fast_router import route_fast_path, should_call_api_for_input


class ProcessQueryNoApiTests(unittest.TestCase):
    def test_process_questions_do_not_call_api(self) -> None:
        for text in ["哪个进程占 CPU", "找出高 CPU 进程", "哪些进程占内存", "kill 进程", "查看进程树"]:
            self.assertTrue(route_fast_path(text).fast, text)
            self.assertFalse(should_call_api_for_input(text), text)


if __name__ == "__main__":
    unittest.main()
