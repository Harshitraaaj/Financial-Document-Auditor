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
