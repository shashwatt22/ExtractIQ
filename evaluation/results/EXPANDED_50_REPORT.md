# Expanded invoice corpus (50 fictional PDFs) — 2026-10-10

A reproducible GitHub Actions run evaluated the first 50 fictional invoices from an **independently authored** public invoice-agent fixture corpus. This includes the initial 20-invoice pilot plus 30 further examples; it is **not a fresh held-out 50-invoice set**.

- Workflow: https://github.com/shashwatt22/ExtractIQ/actions/runs/38070937975
- Source: https://github.com/superintelligenceco/invoice-agent
- Download script: `python evaluation/fetch_heldout_invoice_test.py --count 50`
- Evaluation script: `python evaluation/real_world_eval.py --dataset evaluation/heldout_invoices --output evaluation/results/expanded_50_invoices.json`
- Metrics: invoice type classification; invoice number and total amount fields only.

| Metric | 20-invoice pilot | Expanded 50-invoice set |
|---|---:|---:|
| Document classification accuracy | 95% | **98%** |
| Field precision | 78.38% | **64.37%** |
| Field recall | 72.50% | **56.00%** |
| Field F1 | 75.32% | **59.89%** |
| Correct annotated fields | 29/40 | **56/100** |
| Mean pipeline time per PDF | 0.09 s | **0.09 s** |

The pipeline is the lightweight deterministic backend; Gemini was not invoked. Some PDFs could not use OCR because Tesseract was unavailable in the CI environment. The documents are fictional and reference labels are inherited from the source fixture repository, not independently audited. These results should not be represented as performance on real healthcare or invoice workloads.

Latest evaluation JSON artifact also reports per-field metrics, exact-match counts, classification confusion matrix, and failure categories.

**Next:** collect 100+ *varied* independently labeled invoice documents (different sources, scans and currencies) and conduct a truly untouched evaluation. The requested 100+ benchmark is **not completed**.
