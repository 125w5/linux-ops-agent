from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RpcRequest:
    id: str | int | None
    method: str
    params: dict[str, Any] = field(default_factory=dict)


def parse_line(line: str) -> RpcRequest:
    data = json.loads(line.lstrip("\ufeff"))
    if not isinstance(data, dict):
        raise ValueError("RPC message must be an object")
    method = data.get("method")
    if not isinstance(method, str):
        raise ValueError("RPC message requires string method")
    params = data.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError("RPC params must be an object")
    return RpcRequest(data.get("id"), method, params)


def response(request_id: str | int | None, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: str | int | None, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def event(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "event": event_type, "payload": payload or {}}


def dumps(message: dict[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False, separators=(",", ":"))
