from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from financial_auditor.core.schemas.pipeline import RoutingDecision


@dataclass(frozen=True)
class ReviewTask:
    document_id: str
    tier: str
    due_at_utc: datetime
    reason: str


class HITLQueue:
    def create_task(self, document_id: str, decision: RoutingDecision, reason: str) -> ReviewTask | None:
        if decision == RoutingDecision.AUTO_APPROVE or decision == RoutingDecision.HARD_REJECT:
            return None
        tier = "compliance_officer" if decision == RoutingDecision.COMPLIANCE_HOLD else "junior_analyst"
        sla = timedelta(hours=1) if decision == RoutingDecision.COMPLIANCE_HOLD else timedelta(hours=4)
        return ReviewTask(
            document_id=document_id,
            tier=tier,
            due_at_utc=datetime.now(timezone.utc) + sla,
            reason=reason,
        )

