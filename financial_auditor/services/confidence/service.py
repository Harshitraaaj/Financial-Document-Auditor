from __future__ import annotations

from statistics import fmean

from financial_auditor.core.schemas.documents import PreprocessingResult, VerifiedExtraction
from financial_auditor.core.schemas.findings import Finding, Severity
from financial_auditor.core.schemas.pipeline import (
    AnomalyResult,
    ConfidenceResult,
    FieldConfidence,
    RoutingDecision,
    ValidationResult,
)
from financial_auditor.services.validation.rule_engine.vendor_registry import VendorRegistry


FIELD_CRITICALITY = {
    "total_amount": 1.0,
    "vendor_name": 0.9,
    "invoice_date": 0.8,
    "tax_amount": 0.85,
    "line_items": 0.7,
    "currency": 0.9,
    "invoice_number": 0.9,
}

SEVERITY_PENALTY = {
    Severity.INFO: 0.02,
    Severity.LOW: 0.08,
    Severity.MEDIUM: 0.25,
    Severity.HIGH: 0.55,
    Severity.CRITICAL: 1.0,
}


class ConfidenceService:
    def __init__(self, vendor_registry: VendorRegistry) -> None:
        self.vendor_registry = vendor_registry

    def score(
        self,
        preprocessing: PreprocessingResult,
        extraction: VerifiedExtraction,
        validation: ValidationResult,
        anomaly: AnomalyResult,
    ) -> ConfidenceResult:
        page_quality = _mean([page.ocr_confidence for page in preprocessing.pages], default=0.0)
        field_scores = []
        for field_name, weight in FIELD_CRITICALITY.items():
            annotation = extraction.annotations.get(field_name)
            verifier_score = annotation.confidence if annotation else 0.65
            value = getattr(extraction.invoice, field_name, None)
            schema_success = 1.0 if _has_present_value(value) else 0.0
            score = 0.40 * page_quality + 0.35 * verifier_score + 0.25 * schema_success
            field_scores.append(FieldConfidence(field_name=field_name, score=max(0.0, min(1.0, score)), criticality_weight=weight))

        weighted_mean = sum(item.score * item.criticality_weight for item in field_scores) / sum(
            item.criticality_weight for item in field_scores
        )
        rule_penalty = _rule_penalty(validation.findings + anomaly.flags)
        document_confidence = (
            0.50 * weighted_mean
            + 0.30 * (1 - rule_penalty)
            + 0.20 * (1 - anomaly.deviation_score)
        )
        decision, reason = self._route(document_confidence, validation.findings, anomaly, extraction)
        return ConfidenceResult(
            field_scores=field_scores,
            document_confidence=max(0.0, min(1.0, document_confidence)),
            rule_severity_penalty=rule_penalty,
            anomaly_deviation_score=anomaly.deviation_score,
            routing_decision=decision,
            routing_reason=reason,
        )

    def _route(
        self,
        confidence: float,
        findings: list[Finding],
        anomaly: AnomalyResult,
        extraction: VerifiedExtraction,
    ) -> tuple[RoutingDecision, str]:
        severities = {finding.severity for finding in findings}
        vendor_approved = self.vendor_registry.is_approved(extraction.invoice.vendor_name)
        if any(finding.rule_id == "DUPLICATE_CONFIRMED" for finding in findings):
            return RoutingDecision.HARD_REJECT, "Duplicate invoice confirmed by local index."
        if confidence < 0.50:
            return RoutingDecision.HARD_REJECT, "Document confidence is below hard-reject threshold."
        if Severity.HIGH in severities or Severity.CRITICAL in severities or 0.50 <= confidence < 0.70:
            return RoutingDecision.COMPLIANCE_HOLD, "High-severity finding or low confidence requires compliance hold."
        if confidence >= 0.92 and not severities.intersection({Severity.HIGH, Severity.CRITICAL}) and not anomaly.flags and vendor_approved:
            return RoutingDecision.AUTO_APPROVE, "Confidence and control checks satisfy auto-approval policy."
        return RoutingDecision.HUMAN_REVIEW, "Confidence, findings, anomaly, or vendor approval state requires human review."


def _rule_penalty(findings: list[Finding]) -> float:
    if not findings:
        return 0.0
    return min(1.0, max(SEVERITY_PENALTY[finding.severity] for finding in findings))


def _mean(values: list[float], default: float) -> float:
    return fmean(values) if values else default


def _has_present_value(value: object) -> bool:
    if value is None:
        return False
    if value == "":
        return False
    if isinstance(value, list) and not value:
        return False
    return True
