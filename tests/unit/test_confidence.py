from __future__ import annotations

from financial_auditor.core.schemas.documents import FieldAnnotation, PageQuality, PreprocessingResult, VerifiedExtraction
from financial_auditor.core.schemas.pipeline import AnomalyResult, RoutingDecision, ValidationResult
from financial_auditor.services.confidence import ConfidenceService


class FakeVendorRegistry:
    def is_approved(self, vendor_name):
        return True


def test_high_confidence_clean_invoice_can_auto_approve(valid_invoice):
    preprocessing = PreprocessingResult(
        document_id="doc-1",
        text="invoice text",
        true_document_type="invoice_text",
        pages=[PageQuality(page_number=1, ocr_confidence=1.0)],
    )
    extraction = VerifiedExtraction(
        document_id="doc-1",
        invoice=valid_invoice,
        annotations={
            field: FieldAnnotation(field_name=field, confidence=1.0)
            for field in ["total_amount", "vendor_name", "invoice_date", "tax_amount", "line_items", "currency", "invoice_number"]
        },
    )
    result = ConfidenceService(FakeVendorRegistry()).score(
        preprocessing,
        extraction,
        ValidationResult(findings=[]),
        AnomalyResult(deviation_score=0.0),
    )
    assert result.routing_decision == RoutingDecision.AUTO_APPROVE

