from __future__ import annotations

from pathlib import Path

from diag.utils.paths import project_root


PROMPT_NAMES = [
    "system",
    "planner",
    "chat_router",
    "evidence_qa",
    "report_writer",
    "risk_reviewer",
    "api_config_assistant",
    "action_suggester",
]


def prompt_path(name: str) -> Path:
    return project_root() / "prompts" / f"{name}.md"


def load_prompt(name: str) -> str:
    if name not in PROMPT_NAMES:
        raise ValueError(f"Unknown prompt: {name}")
    return prompt_path(name).read_text(encoding="utf-8")


def load_prompt_pack() -> dict[str, str]:
    return {name: load_prompt(name) for name in PROMPT_NAMES}
