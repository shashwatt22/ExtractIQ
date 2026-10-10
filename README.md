# ExtractIQ

[![Gemini and benchmark tests](https://github.com/shashwatt22/ExtractIQ/actions/workflows/gemini-tests.yml/badge.svg)](https://github.com/shashwatt22/ExtractIQ/actions/workflows/gemini-tests.yml)
[![Expanded invoice benchmark](https://github.com/shashwatt22/ExtractIQ/actions/workflows/expanded-invoice-benchmark.yml/badge.svg)](https://github.com/shashwatt22/ExtractIQ/actions/workflows/expanded-invoice-benchmark.yml)

**Document Intelligence and Information Extraction Platform**

ExtractIQ is a document processing application that converts unstructured PDFs into organized, searchable information. It supports invoices, contracts, financial statements, and court filings, helping users extract important details without manually reviewing entire documents.

**[Live Application](https://extractiq-ai.streamlit.app/)**

## Features

- **Document Classification:** Identifies document types using TF-IDF, Logistic Regression, and keyword-based classification.
- **Information Extraction:** Extracts names, dates, amounts, payment terms, and other relevant fields.
- **Document Search:** Searches uploaded documents using TF-IDF-based retrieval.
- **Question Answering:** Retrieves relevant information and text excerpts from uploaded documents.
- **Table Extraction:** Extracts structured tables from supported PDF layouts.
- **Source Highlighting:** Highlights extracted information within the original PDF when location data is available.
- **Confidence Scoring:** Displays confidence indicators and identifies extraction sources.

## Tech Stack

| Component | Technologies |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| Machine Learning | Scikit-learn, TF-IDF, Logistic Regression |
| PDF Processing | pdfplumber, pypdfium2 |
| Database | SQLite |
| Document Retrieval | TF-IDF, optional ChromaDB |
| Deployment | Streamlit Community Cloud |

## Architecture

```text
PDF Upload
    |
Text Extraction & Processing
    |
Document Classification
    |
Field & Table Extraction
    |
Confidence-Based Result Merging
    |
Storage & Document Indexing
    |
Search, Results & Source Highlighting
```

The hosted application uses the lightweight processing pipeline, which runs directly within Streamlit without requiring a separate FastAPI server.

## Getting Started

**Requirements:** Python 3.10+

```bash
git clone https://github.com/shashwatt22/extractiq.git
cd extractiq
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

The application includes sample documents for testing.

## Project Structure

```text
backend/      APIs, classification, extraction, retrieval
frontend/     Streamlit application and sample documents
models/       Saved classifier and evaluation metadata
training/     Model training scripts
evaluation/   Evaluation scripts and reports
tests/        Automated tests
docs/         Architecture documentation
```

## Limitations

The document classifier was evaluated primarily on synthetic data. Extraction accuracy may vary with unfamiliar document layouts, scanned PDFs, and poor-quality inputs.

Advanced OCR and transformer-based extraction require additional dependencies. The application is intended for demonstration and experimentation rather than production use with sensitive documents.


## Architecture and Gemini consent

```mermaid
flowchart LR
    A[PDF upload] --> B[Text extraction / optional OCR]
    B --> C[TF-IDF + Logistic Regression classification]
    C --> D[Rule-based field extraction]
    D --> E[SQLite + document review/search]
    E --> F{User explicitly consents?}
    F -->|No| G[Local analysis only]
    F -->|Yes| H[Optional contact masking]
    H --> I[Gemini API: summary or JSON]
```

On Streamlit Community Cloud the app uses the embedded extraction backend. Gemini is **not called during normal document ingestion** and requires an API key, a positive consent check, and a deliberate Analyze click. The optional masking step covers common emails and phone-like numbers only; it does not reliably remove names, addresses, patient identifiers, or every sensitive item.

### Responsible AI and healthcare readiness

- External requests are opt-in; the backend Gemini wrapper rejects calls without consent.
- Prompts treat document text as untrusted evidence, require missing fields to be labeled **Not stated**, and display a verification notice.
- These are partial safeguards, **not** proof that the model cannot hallucinate or that its responses are automatically fact-checked.
- Handling clinical documents or insurance claims would additionally require comprehensive PII/PHI detection and redaction, secure storage and retention rules, access controls, encryption, auditing, provider agreements and relevant legal/security review. **The current app is not approved for sensitive healthcare data.**

### Reproducible evaluation

| Data | Document classification | Field extraction F1 | Scope |
|---|---:|---:|---|
| Original 20-document pilot | 95% | 75.32% | Fictional, independently sourced invoices |
| Expanded 50-document evaluation | 98% | 59.89% | Same source, includes original 20; invoice number and total only |
| External 10-invoice fixture set | 90% | 23.08% | International invoice fixtures, development-set result |

See [50-invoice report](evaluation/results/EXPANDED_50_REPORT.md), [initial 20-invoice report](evaluation/results/HELDOUT_REPORT.md), and [external fixture revisions](evaluation/results/EXTERNAL_INVOICE_REVISION.md). Benchmark JSON includes per-field metrics, exact matches, confusion matrices and observable error categories. These benchmarks are not comparable as before-and-after performance gains.

### Latency and external cost

The 50-PDF lightweight deterministic CI run averaged **0.09 seconds per PDF** without Gemini (runner-dependent). Gemini performs **one content-generation request per explicit Analyze click**; model latency, usage tokens and monetary cost have not been measured. API billing and rate limits depend on the configured Google project.

### Next steps

Test 100+ diverse independently annotated real-document examples, audit OCR behavior on scanned PDFs, and benchmark Gemini-only versus rules-only versus hybrid extraction with a separately labeled evaluation. Add robust PHI/PII controls before any sensitive healthcare use.
