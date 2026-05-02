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

1. Upload a document through `POST /documents`.
2. Ingestion stores the original file, hashes it, creates a local SQLite record, and appends an audit event.
3. Preprocessing extracts text and estimates quality.
4. Extraction calls Groq for primary extraction, then a verifier pass.
5. The schema binder coerces results into strict Pydantic models and records field annotations.
6. Validation runs deterministic schema, arithmetic, business-rule, and duplicate checks.
7. Anomaly scoring compares against local vendor baselines.
8. Confidence routing decides auto-approve, human review, compliance hold, or hard reject.
9. Reporting renders machine-readable and human-readable audit outputs.

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

## Version Control

Source-controlled artifacts include application code, Pydantic schema version metadata, tests, YAML rules, prompt templates, and documentation. Local runtime state, secrets, uploaded documents, logs, and SQLite databases are excluded by `.gitignore`.

See `docs/VERSION_CONTROL.md` for rollback and change-management rules.
