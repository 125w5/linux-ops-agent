from diag.core.models import RiskLevel
from diag.core.models import EvidenceItem
from diag.tools.spec import ToolSpec


def register(context):
    context.register_tool(
        ToolSpec(
            "nginx.recent_errors",
            "Read recent nginx journal errors",
            "journalctl -u nginx -n 100",
            RiskLevel.SAFE_READONLY,
            ("service", "service-failed", "nginx"),
        )
    )
    context.register_runbook("nginx_service_triage", ["service.status", "service.logs", "service.ports", "nginx.recent_errors"])
    context.register_analyzer("nginx.error_hint", analyze_nginx_service)


def analyze_nginx_service(results, evidence):
    joined = "\n".join(result.stdout for result in results)
    extra_evidence = []
    suggestions = []
    if "bind()" in joined and "Address already in use" in joined:
        extra_evidence.append(EvidenceItem("nginx_ops", "nginx_plugin_hint", "Nginx plugin confirmed a port binding conflict.", "warning"))
        suggestions.append("Check the process currently bound to port 80 before changing nginx config.")
    return extra_evidence, suggestions
