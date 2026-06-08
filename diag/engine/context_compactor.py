from __future__ import annotations

from typing import Any


def compact_messages(messages: list[dict[str, Any]], keep_last: int = 8) -> dict[str, Any]:
    if len(messages) <= keep_last:
        return {"compacted": False, "summary": "", "messages": messages}
    old = messages[:-keep_last]
    recent = messages[-keep_last:]
    roles = {"user": 0, "assistant": 0, "tool": 0, "system": 0}
    for message in old:
        role = str(message.get("role") or "system")
        roles[role] = roles.get(role, 0) + 1
    summary = "上下文已压缩：保留最近对话；历史包含 user={user}, assistant={assistant}, tool={tool}, system={system}。".format(**roles)
    return {"compacted": True, "summary": summary, "messages": [{"role": "system", "content": summary}, *recent]}
