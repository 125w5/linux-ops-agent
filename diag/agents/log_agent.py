from __future__ import annotations

from diag.agents.base import AgentScope, BaseSubagent


class LogAgent(BaseSubagent):
    scope = AgentScope("LogAgent", "subagent_log", ("ssh-failure", "service"))
