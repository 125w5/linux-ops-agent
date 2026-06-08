from __future__ import annotations

from diag.agents.base import AgentScope, BaseSubagent


class ReportAgent(BaseSubagent):
    scope = AgentScope("ReportAgent", "report_writer", ())
