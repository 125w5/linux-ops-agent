import unittest

from diag.engine.streaming import emit_assistant_stream


class StreamingEventsTests(unittest.TestCase):
    def test_assistant_stream_emits_start_delta_done(self) -> None:
        events: list[tuple[str, dict]] = []
        emit_assistant_stream(lambda event, payload: events.append((event, payload)), "s1", "abcdef")

        self.assertEqual(events[0][0], "AssistantMessageStarted")
        self.assertEqual(events[-1][0], "AssistantMessageDone")
        self.assertEqual("".join(payload.get("delta", "") for event, payload in events if event == "AssistantDelta"), "abcdef")


if __name__ == "__main__":
    unittest.main()
