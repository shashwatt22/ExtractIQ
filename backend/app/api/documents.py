"""Document endpoints: upload, status, results, page preview, delete."""

from __future__ import annotations

import io
import json
import uuid
from pathlib import Path

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     UploadFile)
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..config import settings
from ..database import Document, get_db
from ..rag import store as rag_store
from ..schemas import DocumentOut, ExtractionResultOut, UploadResponse
from ..workers import processor

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_TYPES)}")

    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")
    if not contents:
        raise HTTPException(400, "Empty file")

    if suffix == ".pdf" and not contents.startswith(b"%PDF-"):
        raise HTTPException(422, "Invalid PDF signature")
    if suffix in {".png"} and not contents.startswith(bytes.fromhex("89504e470d0a1a0a")):
        raise HTTPException(422, "Invalid PNG signature")
    if suffix in {".jpg", ".jpeg"} and not contents.startswith(bytes.fromhex("ffd8ff")):
        raise HTTPException(422, "Invalid JPEG signature")

    doc_id = uuid.uuid4().hex
    stored = settings.data_dir / "uploads" / f"{doc_id}{suffix}"
    stored.write_bytes(contents)

    doc = Document(
        id=doc_id,
        filename=file.filename or f"upload{suffix}",
        content_type=file.content_type or "application/octet-stream",
        stored_path=str(stored),
        status="queued",
    )
    db.add(doc)
    db.commit()

    background_tasks.add_task(processor.run, doc_id)
    return UploadResponse(id=doc_id, filename=doc.filename, status="queued")


@router.post("/batch", response_model=list[UploadResponse], status_code=202)
async def upload_batch(
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Queue at most ten documents; validate each using the ordinary endpoint."""
    if not files or len(files) > 10:
        raise HTTPException(422, "Upload between 1 and 10 documents")
    results = []
    for file in files:
        results.append(await upload_document(file, background_tasks, db))
    return results


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [_to_out(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    return _to_out(doc)


@router.get("/{document_id}/result", response_model=ExtractionResultOut)
def get_result(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    if doc.status in ("queued", "processing"):
        raise HTTPException(409, f"Document is still {doc.status}")
    if doc.status == "failed":
        raise HTTPException(422, f"Processing failed: {doc.error}")
    return json.loads(doc.result_json or "{}")


@router.get("/{document_id}/page/{page_number}")
def get_page_image(document_id: str, page_number: int, db: Session = Depends(get_db)):
    """Render one page as PNG (used by the frontend highlight overlay)."""
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    path = doc.stored_path
    try:
        if path.lower().endswith(".pdf"):
            from ..pipeline.ingest import render_pdf_page

            image = render_pdf_page(path, page_number, scale=2.0)
        else:
            from PIL import Image

            image = Image.open(path).convert("RGB")
    except Exception as exc:
        raise HTTPException(422, f"Could not render page: {exc}")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    try:
        Path(doc.stored_path).unlink(missing_ok=True)
    except OSError:
        pass
    rag_store.remove_document(document_id)
    db.delete(doc)
    db.commit()


def _to_out(d: Document) -> DocumentOut:
    return DocumentOut(
        id=d.id, filename=d.filename, content_type=d.content_type,
        status=d.status, error=d.error, doc_type=d.doc_type,
        doc_type_confidence=d.doc_type_confidence, num_pages=d.num_pages,
        is_scanned=bool(d.is_scanned), processing_seconds=d.processing_seconds,
        created_at=d.created_at,
    )
