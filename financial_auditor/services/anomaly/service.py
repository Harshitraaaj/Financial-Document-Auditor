from __future__ import annotations

from decimal import Decimal

from financial_auditor.core.schemas.documents import ExtractedInvoice
from financial_auditor.core.schemas.findings import Finding, Severity
from financial_auditor.core.schemas.pipeline import AnomalyResult
from financial_auditor.services.validation.rule_engine.vendor_registry import VendorRegistry


class AnomalyService:
    def __init__(self, vendor_registry: VendorRegistry) -> None:
        self.vendor_registry = vendor_registry

    def score(self, invoice: ExtractedInvoice) -> AnomalyResult:
        vendor = self.vendor_registry.get_vendor(invoice.vendor_name)
        if not vendor or invoice.total_amount is None:
            return AnomalyResult(deviation_score=0.0)

        baseline = vendor.get("baseline", {})
        mean = _decimal_or_none(baseline.get("mean_total_amount"))
        stddev = _decimal_or_none(baseline.get("stddev_total_amount"))
        if mean is None or stddev in {None, Decimal("0")}:
            return AnomalyResult(deviation_score=0.0)

        z_score = abs((invoice.total_amount - mean) / stddev)
        deviation_score = min(float(z_score / Decimal("5")), 1.0)
        flags: list[Finding] = []
        if z_score >= Decimal("3"):
            flags.append(
                Finding(
                    rule_id="ANOMALY_VENDOR_AMOUNT_ZSCORE",
                    rule_name="Invoice amount is outside vendor baseline",
                    severity=Severity.MEDIUM,
                    expected_value=f"within 3 stddev of {mean}",
                    actual_value=str(invoice.total_amount),
                    field_name="total_amount",
                    explanation=f"Invoice total is {z_score:.2f} standard deviations from the vendor's historical average.",
                    metadata={"z_score": float(z_score), "mean": str(mean), "stddev": str(stddev)},
                )
            )
        return AnomalyResult(flags=flags, deviation_score=deviation_score)


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))

