# AI Financial Document Auditor

Local-first implementation of an enterprise financial document auditor. The system separates LLM extraction from deterministic validation, rule evaluation, confidence routing, reporting, and audit trail logging.

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- Unstructured for local document text extraction
- Groq for LLM extraction and verification
- YAML local rules/config
- Local file storage and logs
- SQLite local metadata/index
- pytest

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:GROQ_API_KEY="your-key"
uvicorn financial_auditor.api.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Frontend Dashboard

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The Vite dev server proxies `/api/*` to the local FastAPI backend at `http://127.0.0.1:8000`.

## Local Processing Flow

The system follows a strict, unidirectional processing pipeline:

**Ingestion → Preprocessing → Extraction → Validation → Anomaly Detection → Confidence Scoring → Routing → Reporting → Audit Trail**

1. **Ingestion**: Upload a document via `POST /documents`. The system stores the original file, generates a hash, creates a local SQLite record, and appends the first audit event.
2. **Preprocessing**: Extracts raw text using Unstructured and estimates document page quality.
3. **Extraction (LLM-only)**: Calls Groq for primary extraction, followed by an independent verifier pass.
4. **Schema Binding**: Coerces the extracted JSON into strict Pydantic models and records field-level extraction annotations, dropping invalid fields while preserving properly-typed nested objects.
5. **Validation (Deterministic)**: Pure deterministic logic. Runs strict schema validation, arithmetic checks, YAML-driven business rules, and duplicate detection. No LLMs are used here.
6. **Anomaly Detection**: Compares extracted values against local vendor historical baselines.
7. **Confidence Scoring & Routing (HITL)**: Assigns final confidence scores based on validation results, and decides the next routing action (auto-approve, human review, compliance hold, or hard reject).
8. **Reporting**: Renders the final outcome into machine-readable JSON and human-readable audit reports.
9. **Audit Trail**: Throughout the process, every single action is appended into a hash-chained, immutable audit log.

## Boundaries

- `services/extraction`: LLM calls only. No business rules.
- `services/validation`: deterministic validation. No LLM calls.
- `services/validation/rule_engine`: YAML-driven business rules.
- `services/reporting`: renders results. Does not decide outcomes.
- `core/audit_trail`: append-only hash-chained audit events.

## Important Environment Variables

- `GROQ_API_KEY`: required for live extraction.
- `FINANCIAL_AUDITOR_ENV`: defaults to `local`.
- `FINANCIAL_AUDITOR_DATA_DIR`: defaults to `./runtime`.
- `GROQ_MODEL`: defaults to `llama-3.1-70b-versatile`.

## Running Tests

```powershell
pytest
```

## Reset Local Runtime Data

```powershell
python reset_runtime_data.py
```

This clears local testing artifacts under `runtime/` and empties SQLite document and duplicate-index tables, allowing the same invoice to be uploaded again without duplicate warnings. Use `--dry-run` to preview what would be cleared.

## Version Control

Source-controlled artifacts include application code, Pydantic schema version metadata, tests, YAML rules, prompt templates, and documentation. Local runtime state, secrets, uploaded documents, logs, and SQLite databases are excluded by `.gitignore`.

See `docs/VERSION_CONTROL.md` for rollback and change-management rules.
