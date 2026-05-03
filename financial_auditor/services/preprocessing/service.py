from __future__ import annotations

import re
from pathlib import Path

import pytesseract
import unstructured_pytesseract
from unstructured.partition.auto import partition

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import PageQuality, PreprocessingResult


from financial_auditor.core.config.settings import get_settings
settings = get_settings()

if settings.tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path
    unstructured_pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path


class PreprocessingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def process(
        self,
        document_id: str,
        path: Path,
        declared_document_type: str,
    ) -> PreprocessingResult:
        suffix = path.suffix.lower()
        true_document_type = self._detect_type(suffix, declared_document_type)

        # Parse document using Unstructured
        elements = partition(filename=str(path))

        text, table_count = self._serialize_elements(elements)
        quality = self._score_quality(text)

        pages = [
            PageQuality(
                page_number=1,
                ocr_confidence=quality,
            )
        ]

        return PreprocessingResult(
            document_id=document_id,
            text=text,
            layout_metadata={
                "source": "unstructured",
                "element_count": len(elements),
                "table_count": table_count,
                "file_suffix": suffix,
            },
            pages=pages,
            true_document_type=true_document_type,
            quality_low=quality < self.settings.ocr_confidence_threshold,
        )

    def _serialize_elements(
        self,
        elements: list[object],
    ) -> tuple[str, int]:
        text_parts: list[str] = []
        table_count = 0

        for index, element in enumerate(elements, start=1):
            raw_text = str(element).strip()

            if not raw_text:
                continue

            category = type(element).__name__
            normalized_text = self._normalize_financial_table_text(raw_text)

            if category.lower() == "table":
                table_count += 1
                text_parts.append(
                    f"[TABLE {table_count}]\n"
                    f"{normalized_text}\n"
                    f"[/TABLE {table_count}]"
                )
            else:
                text_parts.append(
                    f"[ELEMENT {index}: {category}]\n"
                    f"{normalized_text}"
                )

        return "\n\n".join(text_parts), table_count

    @staticmethod
    def _normalize_financial_table_text(text: str) -> str:
        normalized = text

        # Fix merged table rows like: TotalItem1
        normalized = re.sub(
            r"(?i)(total)(item\s+\d+)",
            r"\1\n\2",
            normalized,
        )

        # Fix merged values like: 25.00Item2
        normalized = re.sub(
            r"(?i)(\$?\d+(?:\.\d{2})?)(item\s+\d+)",
            r"\1\n\2",
            normalized,
        )

        # Normalize invoice row structure
        normalized = re.sub(
            r"(?i)(item\s+\d+)\s*(\d+)\s*([$£€₹]\s*\d+(?:\.\d{2})?)",
            r"\1 | \2 | \3",
            normalized,
        )

        # Normalize currency columns
        normalized = re.sub(
            r"([$£€₹]\s*\d+(?:\.\d{2})?)\s+([$£€₹]\s*\d+(?:\.\d{2})?)",
            r"\1 | \2",
            normalized,
        )

        # Clean extra spaces
        normalized = re.sub(r"[ \t]+", " ", normalized)

        return normalized.strip()

    @staticmethod
    def _detect_type(
        suffix: str,
        declared_document_type: str,
    ) -> str:
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

        score = 0.55 * readability + 0.45 * density

        return max(0.0, min(1.0, score))
