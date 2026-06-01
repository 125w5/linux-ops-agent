from __future__ import annotations

from diag.resources.budget import ResourceBudget


def command_allowed(index: int, budget: ResourceBudget) -> bool:
    return index < budget.max_commands_per_session
