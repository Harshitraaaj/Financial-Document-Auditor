from __future__ import annotations

from uuid import uuid4

from financial_auditor.core.audit_trail import AuditTrailWriter
from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import DocumentMetadata
from financial_auditor.core.storage import LocalFileStorage, SQLiteStore


class IngestionGateway:
    def __init__(self, settings: Settings, storage: LocalFileStorage, store: SQLiteStore, audit: AuditTrailWriter) -> None:
        self.settings = settings
        self.storage = storage
        self.store = store
        self.audit = audit

    def ingest(
        self,
        *,
        content: bytes,
        filename: str,
        tenant_id: str,
        submitted_by: str,
        declared_document_type: str,
        cost_center: str | None,
        content_type: str | None,
    ) -> DocumentMetadata:
        if len(content) > self.settings.max_file_size_bytes:
            raise ValueError(f"File exceeds max size of {self.settings.max_file_size_bytes} bytes")
        document_id = str(uuid4())
        path, digest = self.storage.persist(document_id, filename, content)
        metadata = DocumentMetadata(
            document_id=document_id,
            tenant_id=tenant_id,
            submitted_by=submitted_by,
            declared_document_type=declared_document_type,
            cost_center=cost_center,
            original_filename=filename,
            content_type=content_type,
            file_size_bytes=len(content),
            sha256=digest,
            storage_path=path,
        )
        self.store.insert_document(metadata)
        self.audit.append(
            document_id=document_id,
            event_type="document_ingested",
            actor=submitted_by,
            payload={
                "tenant_id": tenant_id,
                "declared_document_type": declared_document_type,
                "sha256": digest,
                "storage_path": str(path),
            },
        )
        return metadata

