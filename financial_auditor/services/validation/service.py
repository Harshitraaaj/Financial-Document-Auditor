from __future__ import annotations

from financial_auditor.core.schemas.documents import VerifiedExtraction
from financial_auditor.core.schemas.pipeline import ValidationResult
from financial_auditor.services.validation.arithmetic_engine import ArithmeticEngine
from financial_auditor.services.validation.duplicate_detector import DuplicateDetector
from financial_auditor.services.validation.rule_engine import RuleEngine
from financial_auditor.services.validation.schema_validator import SchemaValidator


class ValidationPipeline:
    def __init__(
        self,
        schema_validator: SchemaValidator,
        arithmetic_engine: ArithmeticEngine,
        rule_engine: RuleEngine,
        duplicate_detector: DuplicateDetector,
    ) -> None:
        self.schema_validator = schema_validator
        self.arithmetic_engine = arithmetic_engine
        self.rule_engine = rule_engine
        self.duplicate_detector = duplicate_detector

    def validate(self, tenant_id: str, document_id: str, extraction: VerifiedExtraction) -> ValidationResult:
        invoice = extraction.invoice
        findings = []
        findings.extend(self.schema_validator.validate(invoice))
        findings.extend(self.arithmetic_engine.validate(invoice))
        findings.extend(self.rule_engine.evaluate(invoice))
        findings.extend(self.duplicate_detector.validate(tenant_id, document_id, invoice))
        return ValidationResult(findings=findings)

