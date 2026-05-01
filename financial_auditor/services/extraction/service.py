from __future__ import annotations

from pathlib import Path

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import PreprocessingResult, VerifiedExtraction
from financial_auditor.services.extraction.groq_client import GroqLLMClient
from financial_auditor.services.extraction.prompts import load_prompt, render_prompt
from financial_auditor.services.extraction.schema_binder import SchemaBinder


class ExtractionService:
    def __init__(self, settings: Settings, llm_client: GroqLLMClient | None = None) -> None:
        self.settings = settings
        self.llm_client = llm_client or GroqLLMClient(settings)
        self.binder = SchemaBinder()
        self.prompt_dir = Path("prompts")

    def extract(self, preprocessing: PreprocessingResult) -> VerifiedExtraction:
        system_prompt = load_prompt(self.prompt_dir / "extraction" / "invoice_system.md")
        user_template = load_prompt(self.prompt_dir / "extraction" / "invoice_user.md")
        primary_user = render_prompt(
            user_template,
            document_text=preprocessing.text,
            layout_metadata=str(preprocessing.layout_metadata),
        )
        primary_raw = self.llm_client.complete_json(system_prompt, primary_user)

        verifier_system = load_prompt(self.prompt_dir / "verification" / "invoice_system.md")
        verifier_template = load_prompt(self.prompt_dir / "verification" / "invoice_user.md")
        verifier_user = render_prompt(
            verifier_template,
            document_text=preprocessing.text,
            extracted_json=primary_raw,
        )
        verifier_raw = self.llm_client.complete_json(verifier_system, verifier_user)
        return self.binder.bind(preprocessing.document_id, primary_raw, verifier_raw)

