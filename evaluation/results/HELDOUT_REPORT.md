# Untuned independent-source benchmark — October 10, 2026

The lightweight deterministic ExtractIQ pipeline was evaluated on the **first 20 publicly available fictional PDF invoices** from a separate invoice-agent corpus. No vendor-specific tuning was made on these 20 PDFs before this run.

Source: https://github.com/superintelligenceco/invoice-agent
Workflow: https://github.com/shashwatt22/ExtractIQ/actions/runs/38067783095

## Results

| Metric | Held-out score |
|---|---:|
| Documents | 20 |
| Annotated invoice-number and total fields | 40 |
| Correct fields | 29 |
| Wrong extracted fields | 8 |
| Missing or incorrect reference fields | 11 |
| Field precision | 78.38% |
| Field recall | 72.50% |
| Field F1 | **75.32%** |
| Invoice classification accuracy | **95.00%** |
| Mean pipeline time | 0.09 s / PDF |

## Honest interpretation

This is a **separate-source held-out fixture test**, not a real commercial-document study. All invoices in the source corpus are fictional and programmatically created; results do not validate production accuracy. The evaluated fields are limited to invoice number and total, and labels originated from published reference JSON. Extraction of dates, vendors, taxes, line items, OCR and Gemini was not evaluated here. The runner did not have Tesseract installed, so at least one PDF requiring OCR was not processed through OCR. Numeric matching removes symbols/separators and does not validate correct currency identification.

The 75.32% F1 must **not** be equated to 23.08% F1 on the earlier unrelated external invoice2data fixtures as an improvement: the datasets differ in layout difficulty, reference formats, and composition.

Use this result as evidence that a reproducible independent-source evaluation was built and executed, with documented limitations. Do not advertise real-world field extraction accuracy based on synthetic invoices.
