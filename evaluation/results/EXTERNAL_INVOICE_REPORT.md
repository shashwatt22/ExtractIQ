# External Public-Invoice Evaluation — October 10, 2026

A GitHub Actions workflow ran the existing lightweight ExtractIQ pipeline (without Gemini) on 10 externally sourced public invoice PDFs from the invoice2data public comparison fixtures.

- Source: https://github.com/invoice-x/invoice2data/tree/master/tests/compare
- Runner: https://github.com/shashwatt22/ExtractIQ/actions/runs/38067267449
- Reproduction: `evaluation/fetch_public_invoice_test.py` then `evaluation/real_world_eval.py`
- Published upstream reference metadata; **not manually re-annotated or independently audited**.
- Evaluated only fields common to both schemas: `invoice_number`, `total_amount`.
- These PDFs contain varied international layouts, currencies and date formats.
- 10 PDF files, 20 reference field labels.

## Measured results

| Metric | Value |
|---|---:|
| Document-type accuracy | 40% |
| Reference fields correct | 1 / 20 |
| Wrong extracted fields | 2 |
| Missing or incorrectly extracted reference fields | 19 |
| Field precision | 33.33% |
| Field recall | 5.00% |
| Field F1 | 8.70% |
| Mean processing time | 0.374 seconds/PDF |

**Interpretation:** External-invoice generalization is poor. A passing workflow means the benchmark executed successfully, not that the model performed well.

## Limitations

The upstream reference values were published for the invoice2data extractor and not independently human-reviewed for this benchmark. Normalization is strict and may count valid alternate representations as wrong. Partial reference annotation omits other possible extracted fields from scoring. Results represent a small, nonrepresentative sample of 10 invoices, so performance should not be generalized to all business documents. This tested the **deterministic lightweight backend**, not Gemini summarization, Gemini structured extraction, or neural OCR.

## Next engineering directions

1. Analyze failures by document format; improve classification for invoice layouts and number recognition.
2. Normalize currency symbols, numerical formats and invoice identifiers before scoring.
3. Expand to a larger annotated holdout without tuning on test examples.
4. Separately benchmark the optional Gemini JSON extraction with audited references.

Do not claim real-world accuracy improvements or production-level performance based on these results.
