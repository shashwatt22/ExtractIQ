# ExtractIQ

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

## License

MIT License.
