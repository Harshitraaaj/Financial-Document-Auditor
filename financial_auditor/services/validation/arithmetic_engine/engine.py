from __future__ import annotations

from decimal import Decimal

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.core.schemas.findings import Finding, Severity


class ArithmeticEngine:
    def __init__(self, tolerance: Decimal = Decimal("0.02")) -> None:
        self.tolerance = tolerance

    def validate(self, invoice: ExtractedInvoice) -> list[Finding]:
        findings: list[Finding] = []
        line_item_amounts = [item.amount for item in invoice.line_items if item.amount is not None]
        if line_item_amounts and invoice.subtotal_amount is not None:
            expected_subtotal = sum(line_item_amounts, Decimal("0"))
            if abs(expected_subtotal - invoice.subtotal_amount) > self.tolerance:
                findings.append(
                    Finding(
                        rule_id="ARITH_LINE_ITEMS_SUBTOTAL",
                        rule_name="Line items do not match subtotal",
                        severity=Severity.HIGH,
                        expected_value=str(expected_subtotal),
                        actual_value=str(invoice.subtotal_amount),
                        field_name="subtotal_amount",
                        explanation="The subtotal should equal the sum of line item amounts within rounding tolerance.",
                    )
                )
        if (
            invoice.subtotal_amount is not None
            and invoice.tax_amount is not None
            and invoice.total_amount is not None
        ):
            expected_total = invoice.subtotal_amount + invoice.tax_amount
            if abs(expected_total - invoice.total_amount) > self.tolerance:
                findings.append(
                    Finding(
                        rule_id="ARITH_SUBTOTAL_TAX_TOTAL",
                        rule_name="Subtotal plus tax does not match total",
                        severity=Severity.HIGH,
                        expected_value=str(expected_total),
                        actual_value=str(invoice.total_amount),
                        field_name="total_amount",
                        explanation="Invoice total must equal subtotal plus tax within rounding tolerance.",
                    )
                )
        return findings

