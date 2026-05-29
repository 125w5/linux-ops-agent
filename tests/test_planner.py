import unittest

from diag.planner.plan_builder import build_plan


class PlannerTests(unittest.TestCase):
    def test_build_disk_plan_from_chinese_input(self) -> None:
        plan = build_plan("服务器磁盘快满了", "localhost")
        self.assertEqual(plan.task_type, "disk")
        self.assertEqual(plan.steps[0].command, "df -h")


if __name__ == "__main__":
    unittest.main()
