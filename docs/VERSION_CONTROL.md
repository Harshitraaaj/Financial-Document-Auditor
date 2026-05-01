# Version Control and Rollback

This project treats code, schemas, prompts, and rules as source-of-truth artifacts. Runtime files are intentionally excluded from Git.

## Tracked

- Application code: `financial_auditor/`
- Tests: `tests/`
- Rule definitions: `data/rule_definitions/`
- Vendor registry seed data: `data/vendor_registry/`
- Prompt templates: `prompts/`
- Documentation: `README.md`, `docs/`, `CHANGELOG.md`
- Dependency metadata: `pyproject.toml`, `uv.lock`
- Version metadata: `VERSION`, schema registry

## Not Tracked

- `.env` and other secret-bearing files
- `runtime/` logs, uploads, reports, and SQLite database
- virtual environments
- Python caches and package build output
- uploaded financial documents

## Change Discipline

Schema changes:

- Update `financial_auditor/core/schemas/versions.py`.
- Update tests for changed contracts.
- Record the change in `CHANGELOG.md`.
- Use a major version bump when downstream consumers must change.

Rule changes:

- Update YAML rule `version` and `effective_date`.
- Add a short entry in `data/rule_definitions/CHANGELOG.md`.
- Add or update unit tests when rule behavior changes.

Prompt changes:

- Update prompt files under `prompts/`.
- Record material behavioral changes in `CHANGELOG.md`.
- Keep extraction and verification prompts separate.

Rollback:

```powershell
git log --oneline
git checkout <commit-or-tag>
```

Release tags:

```powershell
git tag -a v0.1.0 -m "Local-first baseline"
```

Branching:

- `main`: stable local baseline
- `feature/*`: implementation work
- `rules/*`: rule-only updates
- `schema/*`: schema contract updates

