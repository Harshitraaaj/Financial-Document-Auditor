from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class VendorRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._payload = self._load()

    def is_approved(self, vendor_name: str | None) -> bool:
        vendor = self.get_vendor(vendor_name)
        return bool(vendor and vendor.get("approved"))

    def get_vendor(self, vendor_name: str | None) -> dict[str, Any] | None:
        if not vendor_name:
            return None
        normalized = _normalize(vendor_name)
        for vendor in self._payload.get("vendors", []):
            names = [_normalize(vendor.get("name")), *[_normalize(alias) for alias in vendor.get("aliases", [])]]
            if normalized in names:
                return vendor
        return None

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"vendors": []}
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or {"vendors": []}


def _normalize(value: str | None) -> str:
    return (value or "").strip().casefold()

