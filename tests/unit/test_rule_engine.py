from __future__ import annotations

from datetime import date

from financial_auditor.core.schemas.findings import Severity
from financial_auditor.services.validation.rule_engine import RuleEngine
from financial_auditor.services.validation.rule_engine.models import RuleDefinition


class FakeVendorRegistry:
    def is_approved(self, vendor_name):
        return vendor_name == "Approved Vendor"

    def get_vendor(self, vendor_name):
        return {"tax_rate": "0.20"} if vendor_name == "Approved Vendor" else None


def test_vendor_approved_rule_fires(valid_invoice):
    rule = RuleDefinition(
        rule_id="VENDOR_APPROVED",
        version="1.0.0",
        name="Vendor approved",
        description="Vendor must be approved.",
        effective_date=date(2026, 1, 1),
        severity=Severity.HIGH,
        condition="vendor_approved",
    )
    findings = RuleEngine([rule], FakeVendorRegistry()).evaluate(valid_invoice)
    assert findings[0].rule_id == "VENDOR_APPROVED"

