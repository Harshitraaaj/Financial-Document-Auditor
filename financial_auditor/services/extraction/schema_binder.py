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
            extraction_payload = verifier.get("corrected_invoice", verifier.get("invoice", extraction_payload))
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


def _null_invalid_payload(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = set(ExtractedInvoice.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}

