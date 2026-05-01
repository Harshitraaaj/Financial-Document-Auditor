from __future__ import annotations

import re

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.core.schemas.findings import Finding, Severity
from financial_auditor.core.storage import SQLiteStore


class DuplicateDetector:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def validate(self, tenant_id: str, document_id: str, invoice: ExtractedInvoice) -> list[Finding]:
        fuzzy_key = build_fuzzy_key(invoice)
        if not fuzzy_key:
            return []
        candidates = [row for row in self.store.find_duplicate_candidates(tenant_id, fuzzy_key) if row["document_id"] != document_id]
        if not candidates:
            return []
        return [
            Finding(
                rule_id="DUPLICATE_CONFIRMED",
                rule_name="Duplicate invoice candidate found",
                severity=Severity.CRITICAL,
                expected_value="unique invoice",
                actual_value=f"{len(candidates)} matching prior invoice(s)",
                explanation="The invoice matches prior records on normalized vendor, invoice number, date, currency, and amount.",
                metadata={"matches": [dict(row) for row in candidates[:5]], "similarity_score": 1.0},
            )
        ]


def build_fuzzy_key(invoice: ExtractedInvoice) -> str:
    parts = [
        _normalize(invoice.vendor_name),
        _normalize(invoice.invoice_number),
        invoice.invoice_date.isoformat() if invoice.invoice_date else "",
        invoice.currency or "",
        str(invoice.total_amount) if invoice.total_amount is not None else "",
    ]
    return "|".join(parts)


def _normalize(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())

