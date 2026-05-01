from __future__ import annotations

from functools import lru_cache

from financial_auditor.core.audit_trail import AuditTrailWriter
from financial_auditor.core.config import get_settings
from financial_auditor.core.storage import LocalFileStorage, SQLiteStore
from financial_auditor.pipeline import AuditPipeline
from financial_auditor.services.anomaly import AnomalyService
from financial_auditor.services.confidence import ConfidenceService
from financial_auditor.services.extraction import ExtractionService
from financial_auditor.services.ingestion_gateway import IngestionGateway
from financial_auditor.services.preprocessing import PreprocessingService
from financial_auditor.services.reporting import ReportGenerator
from financial_auditor.services.validation import ValidationPipeline
from financial_auditor.services.validation.arithmetic_engine import ArithmeticEngine
from financial_auditor.services.validation.duplicate_detector import DuplicateDetector
from financial_auditor.services.validation.rule_engine import RuleEngine
from financial_auditor.services.validation.rule_engine.registry import RuleRegistry
from financial_auditor.services.validation.rule_engine.vendor_registry import VendorRegistry
from financial_auditor.services.validation.schema_validator import SchemaValidator


@lru_cache
def get_pipeline() -> AuditPipeline:
    settings = get_settings()
    storage = LocalFileStorage(settings)
    store = SQLiteStore(settings)
    audit = AuditTrailWriter(settings)
    vendor_registry = VendorRegistry(settings.vendor_registry_path)
    rules = RuleRegistry(settings.rule_definitions_dir).load()
    ingestion = IngestionGateway(settings, storage, store, audit)
    preprocessing = PreprocessingService(settings)
    extraction = ExtractionService(settings)
    validation = ValidationPipeline(
        schema_validator=SchemaValidator(),
        arithmetic_engine=ArithmeticEngine(),
        rule_engine=RuleEngine(rules, vendor_registry),
        duplicate_detector=DuplicateDetector(store),
    )
    anomaly = AnomalyService(vendor_registry)
    confidence = ConfidenceService(vendor_registry)
    reporting = ReportGenerator(settings)
    return AuditPipeline(
        settings=settings,
        store=store,
        audit=audit,
        ingestion=ingestion,
        preprocessing=preprocessing,
        extraction=extraction,
        validation=validation,
        anomaly=anomaly,
        confidence=confidence,
        reporting=reporting,
    )

