from __future__ import annotations

from decimal import Decimal

from financial_auditor.services.validation.arithmetic_engine import ArithmeticEngine


def test_valid_invoice_has_no_arithmetic_findings(valid_invoice):
    findings = ArithmeticEngine().validate(valid_invoice)
    assert findings == []


def test_total_mismatch_is_high_severity(valid_invoice):
    valid_invoice.total_amount = Decimal("125.00")
    findings = ArithmeticEngine().validate(valid_invoice)
    assert len(findings) == 1
    assert findings[0].rule_id == "ARITH_SUBTOTAL_TAX_TOTAL"
    assert findings[0].severity == "high"

