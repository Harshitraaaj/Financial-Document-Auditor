from __future__ import annotations

from groq import Groq

from financial_auditor.core.config import Settings


class GroqLLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for live extraction")
        self.settings = settings
        self.client = Groq(api_key=settings.groq_api_key)

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            temperature=self.settings.extraction_temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty response")
        return content

