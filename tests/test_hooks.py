import unittest

from diag.core.models import DiagnosisStep
from diag.executor.local_executor import LocalExecutor
from diag.hooks.before_command import BeforeCommandSafetyHook
from diag.hooks.hook_manager import HookExecutionError, HookManager
from diag.permissions.mode import PermissionMode
from diag.permissions.policy import PermissionPolicy
from diag.runtime.context import RuntimeContext
from diag.runtime.session import RuntimeSession
from diag.runtime.transcript import Transcript
from diag.tools.command_tool import CommandTool
from diag.tools.registry import build_default_registry


class HookTests(unittest.TestCase):
    def test_before_command_calls_safety_checker(self) -> None:
        executor = LocalExecutor(demo=True)
        context = RuntimeContext(
            RuntimeSession("x", "localhost", "disk", PermissionMode.DEMO),
            Transcript("s"),
            build_default_registry(),
            PermissionPolicy(PermissionMode.DEMO),
            HookManager(),
            executor,
            CommandTool(executor),
        )
        decision = BeforeCommandSafetyHook()(context, DiagnosisStep("bad", "Bad", "rm -rf /"))
        self.assertFalse(decision.allowed)

    def test_hook_failure_is_clear(self) -> None:
        def bad_hook() -> None:
            raise ValueError("boom")

        manager = HookManager()
        manager.register("x", bad_hook)
        with self.assertRaisesRegex(HookExecutionError, "failed during x"):
            manager.run("x")


if __name__ == "__main__":
    unittest.main()
