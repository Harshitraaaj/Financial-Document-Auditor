from __future__ import annotations

from financial_auditor.core.audit_trail import AuditTrailWriter
from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import DocumentMetadata, DocumentStatus, VerifiedExtraction
from financial_auditor.core.schemas.pipeline import PipelineResult
from financial_auditor.core.storage import SQLiteStore
from financial_auditor.services.anomaly import AnomalyService
from financial_auditor.services.confidence import ConfidenceService
from financial_auditor.services.extraction import ExtractionService
from financial_auditor.services.ingestion_gateway import IngestionGateway
from financial_auditor.services.preprocessing import PreprocessingService
from financial_auditor.services.reporting import ReportGenerator
from financial_auditor.services.validation import ValidationPipeline
from financial_auditor.services.validation.duplicate_detector import build_fuzzy_key


class AuditPipeline:
    def __init__(
        self,
        settings: Settings,
        store: SQLiteStore,
        audit: AuditTrailWriter,
        ingestion: IngestionGateway,
        preprocessing: PreprocessingService,
        extraction: ExtractionService,
        validation: ValidationPipeline,
        anomaly: AnomalyService,
        confidence: ConfidenceService,
        reporting: ReportGenerator,
    ) -> None:
        self.settings = settings
        self.store = store
        self.audit = audit
        self.ingestion = ingestion
        self.preprocessing = preprocessing
        self.extraction = extraction
        self.validation = validation
        self.anomaly = anomaly
        self.confidence = confidence
        self.reporting = reporting

    def process_upload(
        self,
        *,
        content: bytes,
        filename: str,
        tenant_id: str,
        submitted_by: str,
        declared_document_type: str,
        cost_center: str | None,
        content_type: str | None,
    ) -> PipelineResult:
        metadata = self.ingestion.ingest(
            content=content,
            filename=filename,
            tenant_id=tenant_id,
            submitted_by=submitted_by,
            declared_document_type=declared_document_type,
            cost_center=cost_center,
            content_type=content_type,
        )
        return self.process_ingested(metadata)

    def process_ingested(self, metadata: DocumentMetadata) -> PipelineResult:
        result = PipelineResult(metadata=metadata)
        preprocessing = self.preprocessing.process(
            metadata.document_id,
            metadata.storage_path,
            metadata.declared_document_type,
        )
        result.preprocessing = preprocessing
        self.store.update_status(metadata.document_id, DocumentStatus.PREPROCESSED, preprocessing.true_document_type)
        self.audit.append(metadata.document_id, "document_preprocessed", "system", preprocessing.model_dump(mode="json"))

        if preprocessing.quality_low:
            result.validation = None
            self.audit.append(
                metadata.document_id,
                "quality_low_human_review",
                "system",
                {"ocr_threshold": self.settings.ocr_confidence_threshold, "pages": [page.model_dump() for page in preprocessing.pages]},
            )
            result.report = self.reporting.render(result)
            return result

        extraction = self.extraction.extract(preprocessing)
        result.extraction = extraction
        self.store.update_status(metadata.document_id, DocumentStatus.EXTRACTED)
        self.audit.append(metadata.document_id, "document_extracted", "system", _extraction_audit_payload(extraction))

        validation = self.validation.validate(metadata.tenant_id, metadata.document_id, extraction)
        result.validation = validation
        self.store.update_status(metadata.document_id, DocumentStatus.VALIDATED)
        self.audit.append(metadata.document_id, "document_validated", "system", validation.model_dump(mode="json"))

        anomaly = self.anomaly.score(extraction.invoice)
        result.anomaly = anomaly
        self.audit.append(metadata.document_id, "document_anomaly_scored", "system", anomaly.model_dump(mode="json"))

        confidence = self.confidence.score(preprocessing, extraction, validation, anomaly)
        result.confidence = confidence
        self.audit.append(metadata.document_id, "document_routed", "system", confidence.model_dump(mode="json"))

        self.store.insert_invoice_index(
            metadata.document_id,
            metadata.tenant_id,
            extraction.invoice,
            build_fuzzy_key(extraction.invoice),
        )
        result.report = self.reporting.render(result)
        self.store.update_status(metadata.document_id, DocumentStatus.REPORTED)
        self.audit.append(metadata.document_id, "report_generated", "system", result.report.model_dump(mode="json"))
        return result


def _extraction_audit_payload(extraction: VerifiedExtraction) -> dict:
    return {
        "invoice": extraction.invoice.model_dump(mode="json"),
        "annotations": {key: value.model_dump(mode="json") for key, value in extraction.annotations.items()},
        "raw_primary_response": extraction.raw_primary_response,
        "raw_verifier_response": extraction.raw_verifier_response,
    }

