from __future__ import annotations

from pathlib import Path

import yaml

from financial_auditor.services.validation.rule_engine.models import RuleDefinition


class RuleRegistry:
    def __init__(self, rule_dir: Path) -> None:
        self.rule_dir = rule_dir

    def load(self) -> list[RuleDefinition]:
        rules: list[RuleDefinition] = []
        for path in sorted(self.rule_dir.glob("*.yaml")):
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for item in payload.get("rules", []):
                rules.append(RuleDefinition.model_validate(item))
        return rules

