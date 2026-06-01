from diag.core.models import RiskLevel
from diag.tools.spec import ToolSpec


def register(context):
    context.register_tool(
        ToolSpec(
            "security.accepted_ssh",
            "Collect accepted SSH login records",
            "grep 'Accepted' /var/log/auth.log | tail -50",
            RiskLevel.SAFE_READONLY,
            ("ssh-failure", "ssh-security"),
        )
    )
