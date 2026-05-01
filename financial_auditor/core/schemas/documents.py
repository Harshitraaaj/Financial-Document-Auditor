from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentStatus(StrEnum):
    INGESTED = "ingested"
    PREPROCESSED = "preprocessed"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    REPORTED = "reported"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    document_id: str
    tenant_id: str
    submitted_by: str
    declared_document_type: str
    true_document_type: str | None = None
    cost_center: str | None = None
    original_filename: str
    content_type: str | None = None
    file_size_bytes: int
    sha256: str
    storage_path: Path
    submitted_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: DocumentStatus = DocumentStatus.INGESTED


class PageQuality(BaseModel):
    page_number: int = Field(ge=1)
    ocr_confidence: float = Field(ge=0, le=1)
    notes: list[str] = Field(default_factory=list)


class PreprocessingResult(BaseModel):
    document_id: str
    text: str
    layout_metadata: dict[str, Any] = Field(default_factory=dict)
    pages: list[PageQuality] = Field(default_factory=list)
    true_document_type: str
    quality_low: bool = False


class LineItem(BaseModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal | None = None
    tax_rate: Decimal | None = None


class ExtractedInvoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vendor_name: str | None = None
    vendor_tax_id: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    currency: str | None = None
    subtotal_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    total_amount: Decimal | None = None
    purchase_order: str | None = None
    cost_center: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None


class FieldAnnotation(BaseModel):
    field_name: str
    confidence: float = Field(ge=0, le=1)
    source_quote: str | None = None
    page_number: int | None = None
    discrepancy: str | None = None
    extraction_failure: str | None = None
    hallucination_suspected: bool = False


class VerifiedExtraction(BaseModel):
    document_id: str
    invoice: ExtractedInvoice
    annotations: dict[str, FieldAnnotation] = Field(default_factory=dict)
    raw_primary_response: str | None = None
    raw_verifier_response: str | None = None

