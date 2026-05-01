from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    env: str = Field(default="local", alias="FINANCIAL_AUDITOR_ENV")
    data_dir: Path = Field(default=Path("runtime"), alias="FINANCIAL_AUDITOR_DATA_DIR")
    max_file_size_bytes: int = 20 * 1024 * 1024
    max_pages: int = 50
    ocr_confidence_threshold: float = 0.72
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-70b-versatile", alias="GROQ_MODEL")
    extraction_temperature: float = 0.0
    sqlite_path: Path | None = None

    @property
    def storage_dir(self) -> Path:
        return self.data_dir / "storage"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def audit_log_path(self) -> Path:
        return self.logs_dir / "audit_chain.jsonl"

    @property
    def database_path(self) -> Path:
        return self.sqlite_path or self.data_dir / "financial_auditor.sqlite3"

    @property
    def rule_definitions_dir(self) -> Path:
        return Path("data") / "rule_definitions"

    @property
    def vendor_registry_path(self) -> Path:
        return Path("data") / "vendor_registry" / "vendors.yaml"

    def ensure_local_dirs(self) -> None:
        for directory in [self.data_dir, self.storage_dir, self.reports_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_local_dirs()
    return settings

