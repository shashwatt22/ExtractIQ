# External invoice benchmark — exploratory revision (2026-10-10)

The benchmark used the same **10 external invoice2data PDF fixtures** before and after revisions. This is a **development-set comparison**, NOT an independent held-out generalization test.

| Metric | Initial run | Revised run |
|---|---:|---:|
| Correct annotated fields (20 reference fields) | 1 | 3 |
| Field precision | 33.33% | 50.00% |
| Field recall | 5.00% | 15.00% |
| Field F1 | 8.70% | 23.08% |
| Invoice document-type accuracy | 40% | 90% |
| Average processing time per PDF | 0.374 s | 0.388 s |

- Initial workflow: https://github.com/shashwatt22/ExtractIQ/actions/runs/38067267449
- Revised workflow: https://github.com/shashwatt22/ExtractIQ/actions/runs/38067513681
- Dataset: https://github.com/invoice-x/invoice2data/tree/master/tests/compare
- Changes: multilingual invoice keywords; conservative fallback regexes for invoice number and total; numeric-equivalence normalization when scoring.
- These numbers partly reflect changes to metric normalization, **not only an extractor accuracy gain**. Direct causal attribution is not justified.
- The reference annotations originate from another open-source extractor's fixtures, not new independent annotations.
- Evaluation covers only invoice number and total, and ignores extraneous field outputs not in the reference subset.
- Even after revision, field performance is poor (23.08% F1). No real-world production accuracy claim is warranted.
- The app's Gemini summarization/extraction was not included in these benchmark runs.
- Follow-up: gather a fresh held-out public dataset and manually check labels; do not tune on this same fixture set again.
