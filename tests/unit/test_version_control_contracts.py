from __future__ import annotations

import re
from pathlib import Path

import yaml

from financial_auditor.core.schemas import SCHEMA_REGISTRY


SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_schema_registry_entries_are_semver():
    assert SCHEMA_REGISTRY
    for schema in SCHEMA_REGISTRY.values():
        assert schema.schema_id
        assert SEMVER.match(schema.version)
        assert schema.description


def test_rule_definitions_are_versioned_and_dated():
    rule_paths = sorted(Path("data/rule_definitions").glob("*.yaml"))
    assert rule_paths
    for path in rule_paths:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        for rule in payload["rules"]:
            assert rule["rule_id"]
            assert SEMVER.match(str(rule["version"]))
            assert rule["effective_date"]
            assert rule["jurisdiction"]

