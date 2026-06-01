from __future__ import annotations

import sys
from typing import TextIO

from diag.engine.event_stream import EventStream
from diag.engine.methods import EngineMethods
from diag.engine.protocol import dumps, error_response, parse_line, response
from diag.engine.session_manager import EngineSessionManager
from diag.utils.encoding import configure_utf8_stdio


class RpcServer:
    def __init__(self, stdin: TextIO | None = None, stdout: TextIO | None = None) -> None:
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.events = EventStream(self.write_line)
        self.methods = EngineMethods(EngineSessionManager(), self.events)

    def write_line(self, line: str) -> None:
        self.stdout.write(line + "\n")
        self.stdout.flush()

    def handle_line(self, line: str) -> None:
        request_id = None
        try:
            request = parse_line(line)
            request_id = request.id
            result = self.methods.dispatch(request.method, request.params)
            self.write_line(dumps(response(request.id, result)))
        except Exception as exc:
            self.write_line(dumps(error_response(request_id, -32000, str(exc))))

    def serve(self) -> int:
        configure_utf8_stdio()
        for line in self.stdin:
            if not line.strip():
                continue
            self.handle_line(line)
        return 0


def main() -> int:
    return RpcServer().serve()
