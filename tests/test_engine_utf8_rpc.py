import io
import json
import unittest

from diag.engine.rpc_server import RpcServer


class EngineUtf8RpcTests(unittest.TestCase):
    def test_rpc_server_preserves_chinese_in_json_lines(self) -> None:
        stdout = io.StringIO()
        server = RpcServer(stdin=io.StringIO(), stdout=stdout)
        server.handle_line('{"id":1,"method":"session.start","params":{"target":"localhost","mode":"demo"}}')
        session_id = json.loads(stdout.getvalue().splitlines()[-1])["result"]["session_id"]

        server.handle_line(
            json.dumps(
                {"id": 2, "method": "chat.message", "params": {"session_id": session_id, "text": "为什么要检查磁盘？"}},
                ensure_ascii=False,
            )
        )

        content = stdout.getvalue()
        self.assertIn("为什么要检查磁盘", content)
        self.assertIn("当前会话还没有证据", content)
        self.assertNotIn("\\u4e3a", content)


if __name__ == "__main__":
    unittest.main()
