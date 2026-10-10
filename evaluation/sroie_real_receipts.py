"""SROIE real scanned-receipt benchmark. Not part of synthetic sealed holdout.

SROIE provides annotated 'total' amounts, but does not supply a standard
receipt/invoice-number label. Never manufacture or score a number label.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.pipeline.hybrid import process_document
from backend.app.pipeline.extractors.invoice_ranking import normalize_amount


def score_total(predicted: str | None, expected: str | None) -> str:
    if not expected or not str(expected).strip():
        return "unannotated"
    if not predicted or str(predicted).strip().lower() in {"not found", "not stated"}:
        return "missing_total"
    p, _ = normalize_amount(str(predicted))
    t, _ = normalize_amount(str(expected))
    if p is None or t is None:
        return "normalization_failure"
    return "correct" if p == t else "wrong_total"


def evaluate(limit: int, offset: int = 0) -> dict:
    from datasets import load_dataset
    data = load_dataset("jsdnrs/ICDAR2019-SROIE", split=f"train[{offset}:{offset + limit}]")
    failures = []
    counts = Counter()
    with tempfile.TemporaryDirectory(prefix="sroie_") as tmp:
        for idx, record in enumerate(data):
            image = record["image"].convert("RGB")
            filename = f"receipt_{idx:03}.png"
            target = Path(tmp) / filename
            image.save(target)
            annotated = record.get("entities") or {}
            expected = annotated.get("total") if isinstance(annotated, dict) else None
            try:
                result = process_document(str(target))
                fields = result.get("fields", {})
                total = fields.get("total_amount") or fields.get("total") or {}
                predicted = total.get("value") if isinstance(total, dict) else None
                status = score_total(predicted, expected)
                # A high-level OCR/pipeline error is not a model extraction miss.
            except Exception as exc:
                status = "processing_error"
                predicted = None
                failures.append({"index": idx, "status": status, "type": type(exc).__name__})
            counts[status] += 1
            if status not in {"correct", "unannotated", "processing_error"}:
                failures.append({"index": idx, "status": status,
                                 "expected": expected, "predicted": predicted})
    scored = sum(counts[k] for k in ("correct", "missing_total", "wrong_total", "normalization_failure"))
    return {
        "source": "SROIE real scanned receipt images, annotated totals only",
        "sampled_rows": len(data),
        "offset": offset,
        "partition": "test" if offset == 0 else "development",
        "scored_totals": scored,
        "total_exact_normalized_accuracy": round(counts["correct"] / scored, 4) if scored else None,
        "receipt_number_metric": None,
        "categories": dict(counts),
        "failures": failures,
        "limitations": "Receipt numbers are not annotated in SROIE. This is a real-receipt benchmark, not invoice field-level F1.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("evaluation/results/sroie_60.json"))
    args = parser.parse_args()
    if not 50 <= args.limit <= 100:
        raise SystemExit("Evaluate between 50 and 100 real receipts")
    if args.offset < 0:
        raise SystemExit("Offset must be nonnegative")
    result = evaluate(args.limit, args.offset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "failures"}, indent=2))
