# API

## Health

```http
GET /health
```

Returns local service health.

## Upload Document

```http
POST /documents
Content-Type: multipart/form-data
```

Fields:

- `file`: document file
- `tenant_id`: tenant identifier
- `submitted_by`: user or service identity
- `declared_document_type`: defaults to `invoice`
- `cost_center`: optional

Returns the full `PipelineResult`, including metadata, preprocessing, extraction, validation, anomaly, confidence, and report paths when available.

