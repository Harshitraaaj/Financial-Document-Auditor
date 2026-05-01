from __future__ import annotations

from decimal import Decimal

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.core.schemas.findings import Finding
from financial_auditor.services.validation.rule_engine.models import RuleDefinition
from financial_auditor.services.validation.rule_engine.vendor_registry import VendorRegistry


class RuleEngine:
    def __init__(self, rules: list[RuleDefinition], vendor_registry: VendorRegistry) -> None:
        self.rules = rules
        self.vendor_registry = vendor_registry

    def evaluate(self, invoice: ExtractedInvoice) -> list[Finding]:
        findings: list[Finding] = []
        for rule in self.rules:
            finding = self._evaluate_rule(rule, invoice)
            if finding:
                findings.append(finding)
        return findings

    def _evaluate_rule(self, rule: RuleDefinition, invoice: ExtractedInvoice) -> Finding | None:
        if rule.condition == "vendor_approved":
            if not self.vendor_registry.is_approved(invoice.vendor_name):
                return _finding(rule, "approved vendor", invoice.vendor_name, "vendor_name")
        if rule.condition == "tax_rate_matches_vendor":
            vendor = self.vendor_registry.get_vendor(invoice.vendor_name)
            expected_rate = Decimal(str(vendor.get("tax_rate"))) if vendor and vendor.get("tax_rate") is not None else None
            actual_rate = _invoice_tax_rate(invoice)
            if expected_rate is not None and actual_rate is not None and abs(expected_rate - actual_rate) > Decimal("0.001"):
                return _finding(rule, str(expected_rate), str(actual_rate), "tax_amount")
        if rule.condition == "amount_less_than_or_equal":
            field = rule.field or "total_amount"
            actual = getattr(invoice, field)
            limit = Decimal(str(rule.expected))
            if actual is not None and Decimal(actual) > limit:
                return _finding(rule, str(limit), str(actual), field)
        if rule.condition == "currency_allowed":
            allowed = set(rule.parameters.get("allowed", []))
            if invoice.currency and invoice.currency not in allowed:
                return _finding(rule, sorted(allowed), invoice.currency, "currency")
        return None


def _invoice_tax_rate(invoice: ExtractedInvoice) -> Decimal | None:
    if invoice.subtotal_amount in {None, Decimal("0")} or invoice.tax_amount is None:
        return None
    return invoice.tax_amount / invoice.subtotal_amount


def _finding(rule: RuleDefinition, expected: object, actual: object, field_name: str | None) -> Finding:
    return Finding(
        rule_id=rule.rule_id,
        rule_name=rule.name,
        severity=rule.severity,
        expected_value=expected,
        actual_value=actual,
        field_name=field_name,
        explanation=rule.description,
        metadata={"version": rule.version, "jurisdiction": rule.jurisdiction},
    )

