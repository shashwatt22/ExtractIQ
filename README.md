# ExtractIQ

**Document Intelligence and Information Extraction Platform**

ExtractIQ processes business documents and turns unstructured content into searchable, structured information. It supports invoices, contracts, financial statements, and court filings, making it easier to find relevant details without manually going through entire PDFs.

**[Live Application](https://extractiq-ai.streamlit.app/)**

## Features

- **Document classification:** Identifies document types using TF-IDF, Logistic Regression, and keyword-based classification.
- **Information extraction:** Extracts names, dates, amounts, payment terms, and other document-specific fields.
- **Document search:** Finds relevant information across uploaded documents using TF-IDF retrieval.
- **Question answering:** Returns relevant excerpts and extracted information from documents.
- **Table extraction:** Extracts tabular information from supported PDF layouts.
- **Source highlighting:** Shows where extracted information appears in the original document when location data is available.
- **Confidence scores:** Provides confidence indicators and extraction-source information.

## Tech Stack

| Component | Technologies |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| Machine Learning | Scikit-learn, TF-IDF, Logistic Regression |
| PDF Processing | pdfplumber, pypdfium2 |
| Database | SQLite |
| Document Retrieval | TF-IDF, with optional ChromaDB |
| Deployment | Streamlit Community Cloud |

## How It Works

```text
Document Upload
      |
PDF Parsing and Text Extraction
      |
Document Classification
      |
Field and Table Extraction
      |
Confidence-Based Result Merging
      |
Storage and Document Indexing
      |
Search, Results and Source Highlights
```

The hosted Streamlit version runs the lightweight processing pipeline directly without requiring a separate API server. Advanced OCR and document-understanding models are available as optional components in the full configuration.

## Run Locally

Requires Python 3.10+.

```bash
git clone https://github.com/shashwatt22/extractiq.git
cd extractiq
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

The application includes sample documents for testing without uploading your own files.

## Project Structure

```text
backend/      API, classification, extraction and retrieval
frontend/     Streamlit application and sample documents
models/       Saved classifier and evaluation metadata
training/     Model training scripts
evaluation/   Evaluation scripts and reports
tests/        Automated tests
docs/         Architecture notes and screenshots
```

## Limitations

The included classifier was evaluated primarily on synthetic documents. Results may vary with scanned PDFs, unfamiliar layouts, and poor-quality inputs. Advanced OCR and transformer-based extraction require additional dependencies.

The application is intended as a document-processing prototype rather than a production system for sensitive information.

## Acknowledgments

ExtractIQ is an adapted deployment of the open-source [Document Intelligence project](https://github.com/abhati27/document-intelligence). The original implementation is by Anmol Bhatia and is distributed under the MIT License. See `LICENSE` for the original copyright and permission terms.
