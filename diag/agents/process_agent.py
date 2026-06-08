from __future__ import annotations

from diag.agents.base import AgentScope, BaseSubagent


class ProcessAgent(BaseSubagent):
    scope = AgentScope("ProcessAgent", "subagent_process", ("cpu",))
