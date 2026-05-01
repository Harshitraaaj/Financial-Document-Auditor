from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

from financial_auditor.core.schemas.findings import Severity


class RuleDefinition(BaseModel):
    rule_id: str
    version: str
    name: str
    description: str
    jurisdiction: str = "global"
    effective_date: date
    severity: Severity
    condition: Literal[
        "vendor_approved",
        "tax_rate_matches_vendor",
        "amount_less_than_or_equal",
        "currency_allowed",
    ]
    field: str | None = None
    expected: Any = None
    parameters: dict[str, Any] = Field(default_factory=dict)

