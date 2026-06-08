from __future__ import annotations

from diag.agents.log_agent import LogAgent
from diag.agents.process_agent import ProcessAgent
from diag.agents.report_agent import ReportAgent
from diag.agents.security_agent import SecurityAgent
from diag.agents.service_agent import ServiceAgent


AGENT_TYPES = [LogAgent, ProcessAgent, ServiceAgent, SecurityAgent, ReportAgent]


def list_agents(sandbox_profile: str = "safe-read") -> list[dict[str, object]]:
    return [
        {"name": agent.scope.name, "sandbox_profile": sandbox_profile, "tool_scenes": list(agent.scope.tool_scenes)}
        for agent in (agent_type(sandbox_profile) for agent_type in AGENT_TYPES)
    ]
