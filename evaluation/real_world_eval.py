"""Evaluation on externally sourced, manually annotated business PDFs.

Manifest format:
[
 {"file":"invoice_a.pdf","source_url":"https://...","doc_type":"invoice",
  "fields":{"invoice_number":"INV-12","total_amount":"$100.00"}}
]

Place downloaded PDFs inside the dataset directory. Never score synthetic generated
samples as a real-world benchmark. Ground truth must be annotated independently.
"""
from __future__ import annotations
import argparse
import json
import re
from decimal import Decimal, InvalidOperation
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.pipeline.hybrid import process_document

def normalized(value):
    v=str(value).strip().casefold()
    v=re.sub(r"[$,\s]","",v)
    return v

def score_records(records):
    tp=fp=fn=0
    for item in records:
        predicted=item["predicted"]
        truth=item["truth"]
        for key,expected in truth.items():
            actual=predicted.get(key)
            if actual is None or not str(actual).strip():
                fn+=1
            elif normalized(actual)==normalized(expected):
                tp+=1
            else:
                fp+=1
                fn+=1
        # Predicted named fields absent from the reference schema are
        # ignored rather than labeled false positives: the reference may
        # annotate only a subset. Document this limit in the report.
    p=tp/(tp+fp) if tp+fp else 0
    r=tp/(tp+fn) if tp+fn else 0
    f=2*p*r/(p+r) if p+r else 0
    return {"correct":tp,"wrong":fp,"missed":fn,
            "field_precision":round(p,4),"field_recall":round(r,4),
            "field_f1":round(f,4),
            "note":"Only annotated field names scored; unannotated output fields ignored."}

def breakdown(records):
    """Report each annotated field separately, plus a classification confusion matrix."""
    keys=sorted({key for row in records for key in row["truth"]})
    per_field={}
    for key in keys:
        subset=[{"truth":{key:row["truth"][key]},
                 "predicted":{key:row["predicted"][key]} if key in row["predicted"] else {}}
                for row in records if key in row["truth"]]
        metric=score_records(subset)
        metric["annotated_samples"]=len(subset)
        metric["exact_matches"]=sum(
            str(row["predicted"].get(key,"")).strip()==str(row["truth"][key]).strip()
            for row in records if key in row["truth"]
        )
        per_field[key]=metric
    matrix={}
    for row in records:
        expected=row.get("expected_doc_type")
        if expected:
            predicted=row.get("predicted_doc_type","other")
            matrix.setdefault(expected,{})
            matrix[expected][predicted]=matrix[expected].get(predicted,0)+1
    class_scores={}
    labels=sorted(set(matrix)|{label for x in matrix.values() for label in x})
    for label in labels:
        tp=matrix.get(label,{}).get(label,0)
        fp=sum(matrix.get(other,{}).get(label,0) for other in labels if other!=label)
        fn=sum(count for other,count in matrix.get(label,{}).items() if other!=label)
        precision=tp/(tp+fp) if tp+fp else 0
        recall=tp/(tp+fn) if tp+fn else 0
        class_scores[label]={"support":sum(matrix.get(label,{}).values()),
                             "precision":round(precision,4),"recall":round(recall,4)}
    return {"per_field":per_field,"classification_confusion_matrix":matrix,
            "classification_per_class":class_scores}


def failure_taxonomy(records):
    """Observable error categories, without attributing causes we cannot prove."""
    failures=[]
    for row in records:
        if row.get("expected_doc_type") and row["expected_doc_type"] != row["predicted_doc_type"]:
            failures.append({"file":row["file"],"category":"classification_mismatch",
                             "expected":row["expected_doc_type"],"actual":row["predicted_doc_type"]})
        for name,wanted in row["truth"].items():
            actual=row["predicted"].get(name)
            if not actual:
                reason="missing_field"
            elif normalized(actual)!=normalized(wanted):
                reason="value_mismatch"
            else:
                continue
            failures.append({"file":row["file"],"field":name,"category":reason,
                             "expected":wanted,"actual":actual,
                             "scanned_pdf":row.get("is_scanned",False)})
    counts={}
    for item in failures:
        key=item["category"]
        counts[key]=counts.get(key,0)+1
    return {"counts":counts,"failures":failures,
            "note":"Categories describe observed symptoms, not verified root causes. OCR failures or hallucinations require separate review."}


def run(dataset:Path):
    entries=json.loads((dataset/"manifest.json").read_text(encoding="utf-8"))
    if not isinstance(entries,list) or not entries:
        raise ValueError("Nonempty manifest list required")
    records=[]
    for entry in entries:
        if not entry.get("source_url"):
            raise ValueError(f"Missing original public source URL: {entry.get('file')}")
        path=(dataset/entry["file"]).resolve()
        if not path.is_relative_to(dataset.resolve()) or not path.is_file() or path.suffix.lower()!=".pdf":
            raise ValueError(f"Missing or unsafe PDF path: {entry['file']}")
        started=time.monotonic()
        output=process_document(str(path))
        seconds=round(time.monotonic()-started,3)
        predicted={k:v["value"] for k,v in output["fields"].items()}
        records.append({"file":entry["file"],"source_url":entry["source_url"],
                        "truth":entry["fields"],"predicted":predicted,
                        "expected_doc_type":entry.get("doc_type"),
                        "predicted_doc_type":output["document_type"],
                        "processing_seconds":seconds,
                        "is_scanned":bool(output.get("meta",{}).get("is_scanned",False)),
                        "ingest_source":output.get("meta",{}).get("ingest_source")})
    score=score_records(records)
    score["documents"]=len(records)
    score["mean_processing_seconds"]=round(sum(x["processing_seconds"] for x in records)/len(records),3)
    typed=[x for x in records if x["expected_doc_type"]]
    score["doc_type_accuracy"]=round(sum(x["expected_doc_type"]==x["predicted_doc_type"] for x in typed)/len(typed),4) if typed else None
    return {"summary":score, **breakdown(records), "failure_taxonomy":failure_taxonomy(records), "documents":records}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset",required=True,type=Path)
    parser.add_argument("--output",default="evaluation/results/real_world.json",type=Path)
    args=parser.parse_args()
    result=run(args.dataset)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
