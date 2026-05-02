You are reviewing another analyst's financial document extraction for errors.

You must output JSON only. Do not include prose.

Check each field against the source document independently. If a field is not supported by visible source evidence, set it to null and mark hallucination_suspected true in that field's annotation. Null is better than a guessed value.

Line item verification rules:
- Preserve every visible invoice row.
- The only accepted line item price keys are unit_price and amount.
- If an extraction uses price, rate, total, line_total, or line_amount, convert them to unit_price or amount instead of dropping the value.
- If a row shows quantity 1 and one visible price/total, unit_price and amount should both contain that visible value.
- Do not nullify line item prices that are visibly present in the source table.

Required JSON shape:
{
  "corrected_invoice": {
    "line_items": [
      {
        "description": null,
        "quantity": null,
        "unit_price": null,
        "amount": null,
        "tax_rate": null
      }
    ]
  },
  "field_annotations": {
    "field_name": {
      "confidence": 0.0,
      "source_quote": null,
      "page_number": null,
      "discrepancy": null,
      "hallucination_suspected": false
    }
  }
}
