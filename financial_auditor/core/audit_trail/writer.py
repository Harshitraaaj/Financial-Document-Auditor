from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import uuid4

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.audit import AuditEvent


class AuditTrailWriter:
    def __init__(self, settings: Settings) -> None:
        self.path: Path = settings.audit_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, document_id: str, event_type: str, actor: str, payload: dict) -> AuditEvent:
        previous_hash = self._last_hash()
        event = AuditEvent(
            event_id=str(uuid4()),
            document_id=document_id,
            event_type=event_type,
            actor=actor,
            payload=payload,
            previous_hash=previous_hash,
        )
        event.event_hash = self._hash_event(event)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
        return event

    def _last_hash(self) -> str | None:
        if not self.path.exists():
            return None
        last_line = None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last_line = line
        if last_line is None:
            return None
        return json.loads(last_line).get("event_hash")

    @staticmethod
    def _hash_event(event: AuditEvent) -> str:
        payload = event.model_dump(mode="json", exclude={"event_hash"})
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

