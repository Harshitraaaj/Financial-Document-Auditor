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


def test_schema_binder_merges_partial_verifier_invoice_with_primary_invoice():
    primary_raw = """
    {
      "invoice": {
        "vendor_name": "Albert Sort",
        "invoice_number": "#123456",
        "invoice_date": "2027-10-11",
        "due_date": "2027-11-24",
        "currency": "USD",
        "subtotal_amount": 80.00,
        "tax_amount": 0.00,
        "total_amount": 80.00,
        "purchase_order": "P.O. Number: ",
        "line_items": [
          {"description": "Item 1", "quantity": 1, "unit_price": 25.00, "amount": 25.00}
        ]
      },
      "field_annotations": {}
    }
    """
    verifier_raw = """
    {
      "corrected_invoice": {
        "purchase_order": null,
        "line_items": [
          {"description": "Item 1", "quantity": 1, "unit_price": 25.00, "amount": 25.00},
          {"description": "Item 2", "quantity": 1, "unit_price": 30.00, "amount": 30.00},
          {"description": "Item 3", "quantity": 1, "unit_price": 25.00, "amount": 25.00}
        ]
      },
      "field_annotations": {}
    }
    """
    extraction = SchemaBinder().bind("doc-1", primary_raw, verifier_raw)
    assert extraction.invoice.vendor_name == "Albert Sort"
    assert extraction.invoice.invoice_number == "#123456"
    assert extraction.invoice.currency == "USD"
    assert extraction.invoice.total_amount == Decimal("80.0")
    assert extraction.invoice.purchase_order is None
    assert [item.description for item in extraction.invoice.line_items] == ["Item 1", "Item 2", "Item 3"]


def test_schema_binder_repairs_zero_confidence_when_source_evidence_is_present():
    raw = """
    {
      "invoice": {
        "vendor_name": "Acme Supplies Ltd",
        "invoice_number": "ACM-2026-1050",
        "invoice_date": "2026-05-03",
        "currency": "GBP",
        "subtotal_amount": 2500.00,
        "tax_amount": 500.00,
        "total_amount": 3000.00,
        "line_items": [
          {"description": "Office Printer Paper Boxes", "quantity": 20, "unit_price": 50.00, "amount": 1000.00}
        ]
      },
      "field_annotations": {
        "vendor_name": {
          "confidence": 0.0,
          "source_quote": "Vendor Name: Acme Supplies Ltd",
          "page_number": null,
          "discrepancy": null,
          "hallucination_suspected": false
        },
        "invoice_number": {
          "confidence": 0.0,
          "source_quote": "Invoice Number: ACM-2026-1050",
          "page_number": null,
          "discrepancy": null,
          "hallucination_suspected": false
        },
        "currency": {
          "confidence": 0.0,
          "source_quote": "Currency: GBP",
          "page_number": null,
          "discrepancy": null,
          "hallucination_suspected": false
        },
        "total_amount": {
          "confidence": 0.0,
          "source_quote": "Total Amount: £3000.00",
          "page_number": null,
          "discrepancy": null,
          "hallucination_suspected": false
        }
      }
    }
    """
    extraction = SchemaBinder().bind("doc-1", raw)
    assert extraction.annotations["vendor_name"].confidence == 0.95
    assert extraction.annotations["invoice_number"].confidence == 0.95
    assert extraction.annotations["currency"].confidence == 0.95
    assert extraction.annotations["total_amount"].confidence == 0.95


def test_schema_binder_keeps_zero_confidence_for_hallucinated_or_unsupported_fields():
    raw = """
    {
      "invoice": {
        "vendor_name": "Acme Supplies Ltd",
        "invoice_number": "ACM-2026-1050",
        "invoice_date": "2026-05-03",
        "currency": "GBP",
        "total_amount": 3000.00,
        "purchase_order": "PO-78460",
        "line_items": []
      },
      "field_annotations": {
        "purchase_order": {
          "confidence": 0.0,
          "source_quote": "Purchase Order:",
          "page_number": null,
          "discrepancy": "Purchase order label is present but value is empty",
          "hallucination_suspected": true
        }
      }
    }
    """
    extraction = SchemaBinder().bind("doc-1", raw)
    assert extraction.annotations["purchase_order"].confidence == 0.0


def test_field_annotation_accepts_percent_and_label_confidence_values():
    raw = """
    {
      "invoice": {
        "vendor_name": "Acme Supplies Ltd",
        "invoice_number": "ACM-2026-1050",
        "invoice_date": "2026-05-03",
        "currency": "GBP",
        "total_amount": 3000.00,
        "line_items": []
      },
      "field_annotations": {
        "vendor_name": {
          "confidence": "95%",
          "source_quote": "Vendor Name: Acme Supplies Ltd",
          "page_number": 1,
          "discrepancy": null,
          "hallucination_suspected": false
        },
        "invoice_number": {
          "confidence": "high",
          "source_quote": "Invoice Number: ACM-2026-1050",
          "page_number": 1,
          "discrepancy": null,
          "hallucination_suspected": false
        }
      }
    }
    """
    extraction = SchemaBinder().bind("doc-1", raw)
    assert extraction.annotations["vendor_name"].confidence == 0.95
    assert extraction.annotations["invoice_number"].confidence == 0.9


def test_line_item_derives_missing_amount_from_quantity_and_unit_price():
    item = LineItem(description="Item 1", quantity=Decimal("2"), unit_price=Decimal("12.50"))
    assert item.amount == Decimal("25.00")


def test_preprocessing_normalizes_compressed_invoice_table_rows():
    text = "Description Quantity Price TotalItem 1 1$25.00 $25.00Item 2 1$30.00 $30.00 Item 31 $25.00 $25.00"
    normalized = PreprocessingService(Settings())._normalize_financial_table_text(text)
    assert "Total\nItem 1 | 1 | $25.00 | $25.00" in normalized
    assert "$25.00\nItem 2 | 1 | $30.00 | $30.00" in normalized
