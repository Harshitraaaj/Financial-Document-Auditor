from __future__ import annotations

from decimal import Decimal

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.documents import LineItem
from financial_auditor.services.extraction.schema_binder import SchemaBinder
from financial_auditor.services.preprocessing import PreprocessingService


def test_schema_binder_maps_llm_price_and_total_aliases_to_line_item_fields():
    raw = """
    {
      "invoice": {
        "vendor_name": "Albert Sort",
        "invoice_number": "#123456",
        "invoice_date": "2027-11-10",
        "currency": "USD",
        "subtotal_amount": 80.00,
        "tax_amount": 0.00,
        "total_amount": 80.00,
        "line_items": [
          {"description": "Item 1", "quantity": 1, "price": 25.00, "total": 25.00},
          {"description": "Item 2", "quantity": 1, "price": 30.00, "total": 30.00},
          {"description": "Item 3", "quantity": 1, "price": 25.00, "total": 25.00}
        ]
      },
      "field_annotations": {}
    }
    """
    extraction = SchemaBinder().bind("doc-1", raw)
    assert [item.unit_price for item in extraction.invoice.line_items] == [
        Decimal("25.0"),
        Decimal("30.0"),
        Decimal("25.0"),
    ]
    assert [item.amount for item in extraction.invoice.line_items] == [
        Decimal("25.0"),
        Decimal("30.0"),
        Decimal("25.0"),
    ]


def test_line_item_derives_missing_amount_from_quantity_and_unit_price():
    item = LineItem(description="Item 1", quantity=Decimal("2"), unit_price=Decimal("12.50"))
    assert item.amount == Decimal("25.00")


def test_preprocessing_normalizes_compressed_invoice_table_rows():
    text = "Description Quantity Price TotalItem 1 1$25.00 $25.00Item 2 1$30.00 $30.00 Item 31 $25.00 $25.00"
    normalized = PreprocessingService(Settings())._normalize_financial_table_text(text)
    assert "Total\nItem 1 | 1 | $25.00 | $25.00" in normalized
    assert "$25.00\nItem 2 | 1 | $30.00 | $30.00" in normalized

