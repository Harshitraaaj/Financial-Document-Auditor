from __future__ import annotations

from pathlib import Path

from financial_auditor.core.audit_trail import AuditTrailWriter
from financial_auditor.core.config import Settings


def test_audit_events_are_hash_chained(tmp_path: Path):
    settings = Settings(FINANCIAL_AUDITOR_DATA_DIR=tmp_path)
    settings.ensure_local_dirs()
    writer = AuditTrailWriter(settings)
    first = writer.append("doc-1", "created", "tester", {"a": 1})
    second = writer.append("doc-1", "updated", "tester", {"b": 2})
    assert second.previous_hash == first.event_hash
    assert second.event_hash != first.event_hash

