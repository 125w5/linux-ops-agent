from __future__ import annotations

from diag.agents.base import AgentScope, BaseSubagent


class SecurityAgent(BaseSubagent):
    scope = AgentScope("SecurityAgent", "subagent_security", ("security", "ssh-failure"))
