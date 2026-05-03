from __future__ import annotations

import json
from decimal import Decimal

from financial_auditor.services.extraction.schema_binder import SchemaBinder
from financial_auditor.core.schemas.documents import LineItem

def test_schema_binder_coerces_line_items_even_on_validation_error():
    binder = SchemaBinder()
    
    # We provide a payload that will fail global validation due to an invalid field
    # (e.g. invalid date format), but we ensure that line_items are still
    # correctly coerced into LineItem Pydantic models, NOT left as raw dicts.
    primary_response = {
        "invoice": {
            "invoice_date": "invalid_date_string",
            "line_items": [
                {
                    "description": "Test Item",
                    "amount": 150.50
                }
            ]
        }
    }
    
    extraction = binder.bind(
        document_id="doc-123",
        primary_raw=json.dumps(primary_response)
    )
    
    invoice = extraction.invoice
    assert len(invoice.line_items) == 1
    
    # This specifically prevents the regression where line_items[0] was a dict
    assert isinstance(invoice.line_items[0], LineItem)
    assert invoice.line_items[0].amount == Decimal("150.50")
    
    # The invalid field should just be ignored or None, without breaking other valid fields
    assert invoice.invoice_date is None
