from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from financial_auditor.core.schemas.documents import DocumentMetadata, PreprocessingResult, VerifiedExtraction
from financial_auditor.core.schemas.findings import Finding


class RoutingDecision(StrEnum):
    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    COMPLIANCE_HOLD = "compliance_hold"
    HARD_REJECT = "hard_reject"


class FieldConfidence(BaseModel):
    field_name: str
    score: float = Field(ge=0, le=1)
    criticality_weight: float = Field(gt=0)


class ConfidenceResult(BaseModel):
    field_scores: list[FieldConfidence] = Field(default_factory=list)
    document_confidence: float = Field(ge=0, le=1)
    rule_severity_penalty: float = Field(ge=0, le=1)
    anomaly_deviation_score: float = Field(ge=0, le=1)
    routing_decision: RoutingDecision
    routing_reason: str


class AnomalyResult(BaseModel):
    flags: list[Finding] = Field(default_factory=list)
    deviation_score: float = Field(ge=0, le=1)


class ValidationResult(BaseModel):
    findings: list[Finding] = Field(default_factory=list)


class ReportResult(BaseModel):
    json_report_path: str
    markdown_report_path: str
    summary: str


class PipelineResult(BaseModel):
    metadata: DocumentMetadata
    preprocessing: PreprocessingResult | None = None
    extraction: VerifiedExtraction | None = None
    validation: ValidationResult | None = None
    anomaly: AnomalyResult | None = None
    confidence: ConfidenceResult | None = None
    report: ReportResult | None = None

