# Changelog

All notable changes to this project should be recorded here.

The project follows semantic versioning:

- `MAJOR`: incompatible API, schema, rule, or audit-contract changes
- `MINOR`: backwards-compatible features or new rules/schemas
- `PATCH`: backwards-compatible fixes

## [0.1.0] - 2026-05-02

### Added

- Local-first FastAPI financial document auditor.
- Groq-backed extraction and verification chain.
- Deterministic validation modules for schema, arithmetic, business rules, and duplicate detection.
- YAML rule registry with explicit rule versions and effective dates.
- Local SQLite metadata/index, local file storage, and hash-chained audit trail.
- Confidence routing, anomaly scoring, reporting, and pytest coverage.

## [0.1.1] - 2026-05-02

### Fixed

- Preserved invoice line item prices when LLM output uses common table aliases such as `price` and `total`.
- Improved preprocessing text normalization for compressed invoice table rows.
- Tightened extraction and verification prompts to require `unit_price` and `amount` for line items.

## [0.1.2] - 2026-05-02

### Fixed

- Merged partial verifier invoice responses into primary extraction results instead of replacing the full invoice object.
- Preserved primary fields such as vendor, invoice number, dates, currency, subtotal, and total when verifier only returns corrected fields.

## [0.1.3] - 2026-05-03

### Added

- Added `reset_runtime_data.py` to clear local runtime test data and reset SQLite document and duplicate-index tables.
- Added dry-run support and tests for safe local runtime reset behavior.
