from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from financial_auditor.core.schemas.documents import ExtractedInvoice, FieldAnnotation, VerifiedExtraction


class SchemaBinder:
    def bind(self, document_id: str, primary_raw: str, verifier_raw: str | None = None) -> VerifiedExtraction:
        primary = _loads(primary_raw)
        extraction_payload = primary.get("invoice", primary)
        annotations = _annotations_from_payload(primary.get("field_annotations", {}))

        if verifier_raw:
            verifier = _loads(verifier_raw)
            verifier_payload = verifier.get("corrected_invoice", verifier.get("invoice", {}))
            if not isinstance(verifier_payload, dict):
                raise ValueError("Verifier invoice payload must be a JSON object")
            extraction_payload = _deep_merge(extraction_payload, verifier_payload)
            annotations.update(_annotations_from_payload(verifier.get("field_annotations", {})))

        try:
            invoice = ExtractedInvoice.model_validate(extraction_payload)
        except ValidationError as exc:
            invoice = ExtractedInvoice.model_construct(**_null_invalid_payload(extraction_payload))
            annotations["schema"] = FieldAnnotation(
                field_name="schema",
                confidence=0,
                extraction_failure=str(exc),
            )

        annotations = _repair_annotation_confidence(invoice, annotations)

        return VerifiedExtraction(
            document_id=document_id,
            invoice=invoice,
            annotations=annotations,
            raw_primary_response=primary_raw,
            raw_verifier_response=verifier_raw,
        )


def _loads(raw: str) -> dict[str, Any]:
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError("LLM response must be a JSON object")
    return loaded


def _annotations_from_payload(payload: dict[str, Any]) -> dict[str, FieldAnnotation]:
    annotations: dict[str, FieldAnnotation] = {}
    for field_name, value in payload.items():
        if isinstance(value, dict):
            annotations[field_name] = FieldAnnotation(field_name=field_name, **value)
    return annotations


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _repair_annotation_confidence(
    invoice: ExtractedInvoice,
    annotations: dict[str, FieldAnnotation],
) -> dict[str, FieldAnnotation]:
    repaired = dict(annotations)
    for field_name in ExtractedInvoice.model_fields:
        annotation = repaired.get(field_name)
        if annotation is None:
            continue
        value = getattr(invoice, field_name)
        if _has_source_supported_value(value, annotation):
            repaired[field_name] = annotation.model_copy(update={"confidence": max(annotation.confidence, 0.95)})
    if invoice.line_items:
        line_item_annotations = [
            annotation
            for key, annotation in repaired.items()
            if key.startswith("line_items") and _has_source_supported_value(annotation.source_quote, annotation)
        ]
        if line_item_annotations:
            average = sum(annotation.confidence for annotation in line_item_annotations) / len(line_item_annotations)
            repaired["line_items"] = FieldAnnotation(
                field_name="line_items",
                confidence=max(average, 0.95),
                source_quote="Line item table",
                hallucination_suspected=False,
            )
    return repaired


def _has_source_supported_value(value: Any, annotation: FieldAnnotation) -> bool:
    if value is None or value == "" or value == []:
        return False
    if annotation.confidence > 0:
        return False
    if annotation.hallucination_suspected or annotation.discrepancy or annotation.extraction_failure:
        return False
    return bool(annotation.source_quote and annotation.source_quote.strip())


def _null_invalid_payload(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = set(ExtractedInvoice.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}
