from __future__ import annotations

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.services.validation.schema_validator import SchemaValidator


def test_required_fields_are_reported():
    findings = SchemaValidator().validate(ExtractedInvoice())
    ids = {finding.rule_id for finding in findings}
    assert "SCHEMA_REQUIRED_VENDOR_NAME" in ids
    assert "SCHEMA_REQUIRED_TOTAL_AMOUNT" in ids

