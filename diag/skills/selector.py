from __future__ import annotations

from diag.skills.registry import Skill, SkillRegistry


def normalize_skill_name(value: str | None) -> str | None:
    if not value:
        return None
    return value[1:] if value.startswith("/") else value


def select_skill(registry: SkillRegistry, task_type: str, requested: str | None = None) -> Skill | None:
    requested = normalize_skill_name(requested)
    if requested:
        return registry.get(requested)
    matches = registry.for_scene(task_type)
    return matches[0] if matches else None
