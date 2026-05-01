from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterator

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import DocumentMetadata, DocumentStatus, ExtractedInvoice


class SQLiteStore:
    def __init__(self, settings: Settings) -> None:
        self.path = settings.database_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    declared_document_type TEXT NOT NULL,
                    true_document_type TEXT,
                    cost_center TEXT,
                    original_filename TEXT NOT NULL,
                    content_type TEXT,
                    file_size_bytes INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    submitted_at_utc TEXT NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS invoice_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    vendor_name TEXT,
                    invoice_number TEXT,
                    invoice_date TEXT,
                    currency TEXT,
                    total_amount TEXT,
                    fuzzy_key TEXT NOT NULL,
                    created_at_utc TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def insert_document(self, metadata: DocumentMetadata) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id, tenant_id, submitted_by, declared_document_type,
                    true_document_type, cost_center, original_filename, content_type,
                    file_size_bytes, sha256, storage_path, submitted_at_utc, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata.document_id,
                    metadata.tenant_id,
                    metadata.submitted_by,
                    metadata.declared_document_type,
                    metadata.true_document_type,
                    metadata.cost_center,
                    metadata.original_filename,
                    metadata.content_type,
                    metadata.file_size_bytes,
                    metadata.sha256,
                    str(metadata.storage_path),
                    metadata.submitted_at_utc.isoformat(),
                    metadata.status.value,
                ),
            )

    def update_status(self, document_id: str, status: DocumentStatus, true_document_type: str | None = None) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE documents SET status = ?, true_document_type = COALESCE(?, true_document_type) WHERE document_id = ?",
                (status.value, true_document_type, document_id),
            )

    def insert_invoice_index(self, document_id: str, tenant_id: str, invoice: ExtractedInvoice, fuzzy_key: str) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO invoice_index (
                    document_id, tenant_id, vendor_name, invoice_number, invoice_date,
                    currency, total_amount, fuzzy_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    tenant_id,
                    invoice.vendor_name,
                    invoice.invoice_number,
                    _date_to_text(invoice.invoice_date),
                    invoice.currency,
                    _decimal_to_text(invoice.total_amount),
                    fuzzy_key,
                ),
            )

    def find_duplicate_candidates(self, tenant_id: str, fuzzy_key: str) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT * FROM invoice_index
                    WHERE tenant_id = ? AND fuzzy_key = ?
                    ORDER BY created_at_utc DESC
                    LIMIT 25
                    """,
                    (tenant_id, fuzzy_key),
                )
            )


def _decimal_to_text(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None

