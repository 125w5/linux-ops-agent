import unittest

from diag.skills.loader import SkillLoader
from diag.skills.selector import normalize_skill_name, select_skill


class SkillsTests(unittest.TestCase):
    def test_loader_and_selector(self) -> None:
        registry = SkillLoader().load()
        skill = select_skill(registry, "disk")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.risk_max, "safe_readonly")  # type: ignore[union-attr]

    def test_slash_skill_normalization(self) -> None:
        self.assertEqual(normalize_skill_name("/ssh-security"), "ssh-security")


if __name__ == "__main__":
    unittest.main()
