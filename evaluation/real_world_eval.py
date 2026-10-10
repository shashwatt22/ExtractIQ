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
                        "processing_seconds":seconds})
    score=score_records(records)
    score["documents"]=len(records)
    score["mean_processing_seconds"]=round(sum(x["processing_seconds"] for x in records)/len(records),3)
    typed=[x for x in records if x["expected_doc_type"]]
    score["doc_type_accuracy"]=round(sum(x["expected_doc_type"]==x["predicted_doc_type"] for x in typed)/len(typed),4) if typed else None
    return {"summary":score,"documents":records}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset",required=True,type=Path)
    parser.add_argument("--output",default="evaluation/results/real_world.json",type=Path)
    args=parser.parse_args()
    result=run(args.dataset)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))
