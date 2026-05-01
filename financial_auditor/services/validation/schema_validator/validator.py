from __future__ import annotations

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.core.schemas.findings import Finding, Severity


class SchemaValidator:
    REQUIRED_FIELDS = {
        "vendor_name": "Vendor name",
        "invoice_number": "Invoice number",
        "invoice_date": "Invoice date",
        "currency": "Currency",
        "total_amount": "Total amount",
    }

    def validate(self, invoice: ExtractedInvoice) -> list[Finding]:
        findings: list[Finding] = []
        for field_name, label in self.REQUIRED_FIELDS.items():
            if getattr(invoice, field_name) in {None, ""}:
                findings.append(
                    Finding(
                        rule_id=f"SCHEMA_REQUIRED_{field_name.upper()}",
                        rule_name=f"Required field missing: {label}",
                        severity=Severity.MEDIUM,
                        expected_value="present",
                        actual_value=None,
                        field_name=field_name,
                        explanation=f"{label} is required for audit validation and routing.",
                    )
                )
        if invoice.currency and len(invoice.currency) != 3:
            findings.append(
                Finding(
                    rule_id="SCHEMA_CURRENCY_ISO",
                    rule_name="Currency must be ISO-4217",
                    severity=Severity.MEDIUM,
                    expected_value="3-letter currency code",
                    actual_value=invoice.currency,
                    field_name="currency",
                    explanation="Currency must be normalized before financial thresholds and duplicate checks can be trusted.",
                )
            )
        return findings

