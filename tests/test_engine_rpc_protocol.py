import json
import unittest

from diag.engine.protocol import dumps, error_response, event, parse_line, response


class EngineRpcProtocolTests(unittest.TestCase):
    def test_parse_request_and_utf8_dump(self) -> None:
        request = parse_line('\ufeff{"id":1,"method":"chat.message","params":{"text":"检查磁盘"}}')

        self.assertEqual(request.id, 1)
        self.assertEqual(request.method, "chat.message")
        self.assertEqual(request.params["text"], "检查磁盘")

        encoded = dumps(response(request.id, {"message": "检查磁盘"}))
        self.assertIn("检查磁盘", encoded)
        self.assertNotIn("\\u68c0", encoded)
        self.assertEqual(json.loads(encoded)["result"]["message"], "检查磁盘")

    def test_event_and_error_shape(self) -> None:
        self.assertEqual(event("SessionStarted", {"session_id": "s"})["event"], "SessionStarted")
        error = error_response("x", -32000, "boom")
        self.assertEqual(error["jsonrpc"], "2.0")
        self.assertEqual(error["error"]["message"], "boom")


if __name__ == "__main__":
    unittest.main()
