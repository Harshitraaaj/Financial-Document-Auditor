from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile

from financial_auditor.api.dependencies import get_pipeline
from financial_auditor.core.config import get_settings
from financial_auditor.core.logging import configure_logging
from financial_auditor.core.schemas.pipeline import PipelineResult
from financial_auditor.pipeline import AuditPipeline

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title="AI Financial Document Auditor",
    version="0.1.0",
    description="Local-first auditable financial document extraction, validation, routing, and reporting.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.env}


@app.post("/documents", response_model=PipelineResult)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    submitted_by: str = Form(...),
    declared_document_type: str = Form("invoice"),
    cost_center: str | None = Form(None),
    pipeline: AuditPipeline = Depends(get_pipeline),
) -> PipelineResult:
    content = await file.read()
    try:
        return pipeline.process_upload(
            content=content,
            filename=file.filename or "document.bin",
            tenant_id=tenant_id,
            submitted_by=submitted_by,
            declared_document_type=declared_document_type,
            cost_center=cost_center,
            content_type=file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

