# Real-World Document Evaluation (not yet executed)

Unlike `evaluation/generate_dataset.py`, this benchmark **does not generate synthetic documents**. It requires a separately obtained, real/public PDF set and manually verified reference labels.

## Dataset

Create a local directory `evaluation/real_docs/` with actual publicly shareable native PDF invoices/contracts. Do not use confidential documents.

Create `evaluation/real_docs/manifest.json`:

```json
[
  {
    "file": "invoice1.pdf",
    "source_url": "https://example.org/original-public-pdf",
    "doc_type": "invoice",
    "fields": {
      "invoice_number": "INV-001",
      "total_amount": "$100.00",
      "invoice_date": "2026-01-02"
    }
  }
]
```

Use an actual working public source URL, not the placeholder. Labels must be transcribed/verified from the original PDFs **before** measuring the model. Do not tune on test samples. Document sample size, selection criteria and any OCR failures.

## Run

```bash
python -m pip install -r requirements-lite.txt
python evaluation/real_world_eval.py --dataset evaluation/real_docs --output evaluation/results/real_world.json
```

## Measures

- Field precision, recall and F1 on **annotated key names only**. A wrong field counts as one FP and one FN.
- Document type accuracy (for labeled types).
- Average elapsed pipeline time per document.

Matching currently uses strict case-insensitive, punctuation-light normalization, so semantically equivalent dates in different formats may be scored wrong. This is a limitation worth reporting.

**There is no real-world benchmark number yet.** Do not quote synthetic 100% accuracy as performance on real documents, and do not claim that real-world evaluation is complete until data and a saved result are available.
