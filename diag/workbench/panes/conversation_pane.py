from __future__ import annotations

from diag.workbench.state import WorkbenchState


def render_conversation_pane(state: WorkbenchState) -> str:
    if not state.messages:
        return "ConversationPane\n- 输入自然语言生成 plan，/run 执行。"
    lines = ["ConversationPane"]
    for message in state.messages[-8:]:
        lines.append(f"- {message.role}: {message.content}")
    return "\n".join(lines)
