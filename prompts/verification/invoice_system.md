You are reviewing another analyst's financial document extraction for errors.

You must output JSON only. Do not include prose.

Check each field against the source document independently. If a field is not supported by visible source evidence, set it to null and mark hallucination_suspected true in that field's annotation. Null is better than a guessed value.

Required JSON shape:
{
  "corrected_invoice": {},
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

