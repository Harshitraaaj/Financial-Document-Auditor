from __future__ import annotations

from decimal import Decimal

import pytest

from financial_auditor.core.schemas.documents import ExtractedInvoice, LineItem


@pytest.fixture
def valid_invoice() -> ExtractedInvoice:
    return ExtractedInvoice(
        vendor_name="Acme Supplies Ltd",
        invoice_number="INV-1001",
        invoice_date="2026-04-20",
        currency="GBP",
        subtotal_amount=Decimal("100.00"),
        tax_amount=Decimal("20.00"),
        total_amount=Decimal("120.00"),
        line_items=[LineItem(description="Paper", quantity=Decimal("10"), unit_price=Decimal("10.00"), amount=Decimal("100.00"))],
    )

