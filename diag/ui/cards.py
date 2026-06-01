from __future__ import annotations

from diag.core.models import EvidenceItem
from diag.ui.charts import risk_bar


def evidence_card(item: EvidenceItem) -> str:
    return f"[{item.severity}] {item.evidence_type} ({item.source})\n  {item.content}"


def risk_card(risk: str) -> str:
    return risk_bar(risk)
