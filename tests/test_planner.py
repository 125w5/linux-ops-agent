import unittest

from diag.planner.plan_builder import build_plan


class PlannerTests(unittest.TestCase):
    def test_build_disk_plan_from_chinese_input(self) -> None:
        plan = build_plan("服务器磁盘快满了", "localhost")
        self.assertEqual(plan.task_type, "disk")
        self.assertEqual(plan.steps[0].command, "df -h")

    def test_build_ssh_failure_plan_from_chinese_input(self) -> None:
        plan = build_plan("ssh\u5931\u8d25\u68c0\u6d4b", "localhost")

        self.assertEqual(plan.task_type, "ssh-failure")
        self.assertTrue(any("Failed password" in step.command or "auth.log" in step.command for step in plan.steps))
        self.assertFalse(any(step.command == "df -h" for step in plan.steps))

    def test_build_ssh_failure_plan_from_english_input(self) -> None:
        plan = build_plan("ssh failed password login problem", "localhost")

        self.assertEqual(plan.task_type, "ssh-failure")
        self.assertFalse(any(step.command == "df -h" for step in plan.steps))


if __name__ == "__main__":
    unittest.main()
