from __future__ import annotations

import sqlite3
from pathlib import Path

from financial_auditor.core.config import Settings
from financial_auditor.core.storage import SQLiteStore
from reset_runtime_data import reset_runtime_data


def test_reset_runtime_data_clears_runtime_dirs_and_duplicate_index(tmp_path: Path):
    settings = Settings(FINANCIAL_AUDITOR_DATA_DIR=tmp_path)
    settings.ensure_local_dirs()
    audit_trail_dir = tmp_path / "audit_trail"
    audit_trail_dir.mkdir()
    (settings.storage_dir / "invoice.pdf").write_text("invoice", encoding="utf-8")
    (settings.reports_dir / "audit_report.json").write_text("{}", encoding="utf-8")
    (settings.logs_dir / "audit_chain.jsonl").write_text("{}", encoding="utf-8")
    (audit_trail_dir / "event.jsonl").write_text("{}", encoding="utf-8")

    store = SQLiteStore(settings)
    with store.connect() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id, tenant_id, submitted_by, declared_document_type,
                original_filename, file_size_bytes, sha256, storage_path,
                submitted_at_utc, status
            ) VALUES ('doc-1', 'tenant', 'tester', 'invoice', 'invoice.pdf', 7, 'hash', 'path', '2026-05-03T00:00:00Z', 'reported')
            """
        )
        connection.execute(
            """
            INSERT INTO invoice_index (
                document_id, tenant_id, vendor_name, invoice_number,
                invoice_date, currency, total_amount, fuzzy_key
            ) VALUES ('doc-1', 'tenant', 'Vendor', 'INV-1', '2026-05-03', 'USD', '10.00', 'duplicate-key')
            """
        )

    summary = reset_runtime_data(settings)

    assert settings.storage_dir.exists()
    assert settings.reports_dir.exists()
    assert settings.logs_dir.exists()
    assert audit_trail_dir.exists()
    assert not any(settings.storage_dir.iterdir())
    assert not any(settings.reports_dir.iterdir())
    assert not any(settings.logs_dir.iterdir())
    assert not any(audit_trail_dir.iterdir())
    assert set(summary.reset_tables) == {"documents", "invoice_index"}

    with sqlite3.connect(settings.database_path) as connection:
        document_count = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        duplicate_count = connection.execute("SELECT COUNT(*) FROM invoice_index").fetchone()[0]
    assert document_count == 0
    assert duplicate_count == 0


def test_reset_runtime_data_dry_run_preserves_files(tmp_path: Path):
    settings = Settings(FINANCIAL_AUDITOR_DATA_DIR=tmp_path)
    settings.ensure_local_dirs()
    marker = settings.storage_dir / "invoice.pdf"
    marker.write_text("invoice", encoding="utf-8")

    reset_runtime_data(settings, dry_run=True)

    assert marker.exists()

