# Architecture

The local implementation follows the enterprise boundary model:

- `ingestion_gateway`: file intake, SHA-256 hashing, local storage, SQLite metadata, audit append.
- `preprocessing`: document type detection, Unstructured text extraction, quality scoring.
- `extraction`: Groq LLM primary extraction and verifier pass. No business rules.
- `validation`: deterministic schema, arithmetic, business-rule, and duplicate checks. No LLM calls.
- `anomaly`: statistical scoring against vendor baselines.
- `confidence`: field and document confidence aggregation plus routing.
- `hitl`: review queue domain model.
- `reporting`: JSON and Markdown report rendering from prior-stage outputs.
- `audit_trail`: append-only JSONL hash chain.

## Local Runtime

Runtime files are written under `runtime/` by default:

- `runtime/storage`: uploaded originals
- `runtime/reports`: generated reports
- `runtime/logs`: app and audit-chain logs
- `runtime/financial_auditor.sqlite3`: document metadata and duplicate index

## Production Constraints Preserved Locally

- Validation has no dependency on Groq, FastAPI, files, or network.
- Rule definitions are YAML and versioned.
- The LLM verifier can nullify unsupported fields.
- Duplicate detection uses a local exact fuzzy key now, with the interface isolated for later vector similarity.
- Reports explain findings but do not decide outcomes.

