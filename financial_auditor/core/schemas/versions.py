from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaVersion:
    schema_id: str
    version: str
    description: str


SCHEMA_REGISTRY: dict[str, SchemaVersion] = {
    "invoice.extracted": SchemaVersion(
        schema_id="invoice.extracted",
        version="1.0.0",
        description="Structured invoice fields produced by extraction and consumed by deterministic validation.",
    ),
    "finding.validation": SchemaVersion(
        schema_id="finding.validation",
        version="1.0.0",
        description="Structured finding emitted by validation, rule, duplicate, and anomaly checks.",
    ),
    "audit.event": SchemaVersion(
        schema_id="audit.event",
        version="1.0.0",
        description="Append-only audit trail event with hash-chain metadata.",
    ),
    "pipeline.result": SchemaVersion(
        schema_id="pipeline.result",
        version="1.0.0",
        description="End-to-end local pipeline result returned by the API and reporting layer.",
    ),
}


def get_schema_version(schema_id: str) -> SchemaVersion:
    return SCHEMA_REGISTRY[schema_id]

