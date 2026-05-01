from __future__ import annotations

import hashlib
from pathlib import Path

from financial_auditor.core.config import Settings


class LocalFileStorage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_local_dirs()

    def persist(self, document_id: str, filename: str, content: bytes) -> tuple[Path, str]:
        digest = hashlib.sha256(content).hexdigest()
        safe_name = Path(filename).name or "document.bin"
        document_dir = self.settings.storage_dir / document_id
        document_dir.mkdir(parents=True, exist_ok=True)
        path = document_dir / safe_name
        path.write_bytes(content)
        return path, digest

