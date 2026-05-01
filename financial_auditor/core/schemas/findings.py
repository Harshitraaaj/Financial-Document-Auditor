from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    rule_id: str
    rule_name: str
    severity: Severity
    expected_value: Any = None
    actual_value: Any = None
    explanation: str
    field_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

