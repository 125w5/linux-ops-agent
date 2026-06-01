from __future__ import annotations

from pathlib import Path

from diag.skills.registry import Skill, SkillRegistry
from diag.utils.config_loader import parse_simple_yaml
from diag.utils.paths import project_root


def skills_root() -> Path:
    return project_root() / ".opspilot" / "skills"


def _parse_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, object] = {}
    body = text
    if text.startswith("---"):
        _, frontmatter, body = text.split("---", 2)
        metadata = parse_simple_yaml(frontmatter)
    return Skill(
        name=str(metadata.get("name") or path.parent.name),
        description=str(metadata.get("description", "")),
        risk_max=str(metadata.get("risk_max", "safe_readonly")),
        scenes=list(metadata.get("scenes", [])),
        content=body.strip(),
    )


class SkillLoader:
    def load(self) -> SkillRegistry:
        registry = SkillRegistry()
        root = skills_root()
        if not root.exists():
            return registry
        for path in sorted(root.glob("*/SKILL.md")):
            registry.register(_parse_skill(path))
        return registry
