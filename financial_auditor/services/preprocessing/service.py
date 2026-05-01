from __future__ import annotations

from pathlib import Path

from unstructured.partition.auto import partition

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import PageQuality, PreprocessingResult


class PreprocessingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def process(self, document_id: str, path: Path, declared_document_type: str) -> PreprocessingResult:
        suffix = path.suffix.lower()
        true_document_type = self._detect_type(suffix, declared_document_type)
        elements = partition(filename=str(path))
        text_parts = [str(element).strip() for element in elements if str(element).strip()]
        text = "\n".join(text_parts)
        quality = self._score_quality(text)
        pages = [PageQuality(page_number=1, ocr_confidence=quality)]
        return PreprocessingResult(
            document_id=document_id,
            text=text,
            layout_metadata={"source": "unstructured", "element_count": len(elements), "file_suffix": suffix},
            pages=pages,
            true_document_type=true_document_type,
            quality_low=quality < self.settings.ocr_confidence_threshold,
        )

    @staticmethod
    def _detect_type(suffix: str, declared_document_type: str) -> str:
        if suffix == ".pdf":
            return "invoice_pdf"
        if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
            return "invoice_image"
        if suffix in {".txt", ".md"}:
            return "invoice_text"
        return declared_document_type or "unknown"

    @staticmethod
    def _score_quality(text: str) -> float:
        if not text.strip():
            return 0.0
        alpha_numeric = sum(character.isalnum() for character in text)
        printable = sum(character.isprintable() for character in text)
        density = min(len(text) / 1000, 1.0)
        readability = alpha_numeric / max(printable, 1)
        return max(0.0, min(1.0, 0.55 * readability + 0.45 * density))

