from __future__ import annotations

from diag.agents.base import AgentScope, BaseSubagent


class ServiceAgent(BaseSubagent):
    scope = AgentScope("ServiceAgent", "subagent_service", ("service", "systemd", "nginx"))
