"""Development-only ablation; never touches evaluation/diverse_synthetic/sealed_holdout.

Examples:
python evaluation/ablation.py --dataset evaluation/diverse_synthetic/development --limit 30
# External calls are paid and ONLY enabled explicitly:
GEMINI_API_KEY=... python evaluation/ablation.py --dataset ... --limit 10 --allow-gemini

Classifier-only has NO field-extraction F1 by design. Avoid misleading rankings.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.pipeline.classifier import classify_detailed
from backend.app.pipeline.hybrid import process_document
from backend.app.pipeline.ingest import ingest
from backend.app.pipeline.extractors.rules import RulesExtractor
from evaluation.real_world_eval import score_records

def evaluate(dataset:Path,limit:int=30,allow_gemini:bool=False)->dict:
    path=dataset.resolve()
    if "sealed_holdout" in path.parts:
        raise ValueError("Sealed holdout evaluation is forbidden in development ablations")
    entries=json.loads((path/"manifest.json").read_text(encoding="utf-8"))
    if not 1<=limit<=len(entries):
        raise ValueError("limit outside available development examples")
    entries=entries[:limit]
    modes=["rules_only","classifier_only","hybrid"]
    if allow_gemini:
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY required for explicitly enabled Gemini mode")
        modes.append("gemini_only")
    results={}
    for mode in modes:
        records=[]
        errors=[]
        elapsed=0.
        calls=0
        for row in entries:
            pdf=path/row["file"]
            if not pdf.resolve().is_relative_to(path) or not pdf.is_file():
                raise ValueError("Invalid dataset path")
            began=time.monotonic()
            predicted={}
            expected_type=row.get("doc_type")
            try:
                if mode=="hybrid":
                    result=process_document(str(pdf))
                    predicted={k:v["value"] for k,v in result["fields"].items()}
                    doc_type=result["document_type"]
                else:
                    document=ingest(str(pdf))
                    doc_type=classify_detailed(document.full_text)["type"]
                    if mode=="rules_only":
                        predicted={field.name:field.value for field in
                                   RulesExtractor().extract(document,doc_type)
                                   if field.confidence>=.6}
                    elif mode=="gemini_only":
                        from frontend.gemini_features import analyze_with_consent
                        calls+=1
                        output=analyze_with_consent(document.full_text,"invoice_fields",
                                                    os.environ["GEMINI_API_KEY"],consent=True)
                        predicted=output["result"]
            except Exception as exc:
                errors.append({"file":row["file"],"error":type(exc).__name__})
                doc_type="error"
                predicted={}
            elapsed+=time.monotonic()-began
            records.append({
                "file":row["file"],"truth":row["fields"],"predicted":predicted,
                "expected_doc_type":expected_type,"predicted_doc_type":doc_type,
            })
        class_rows=[record for record in records if record["expected_doc_type"]]
        accuracy=(sum(x["expected_doc_type"]==x["predicted_doc_type"] for x in class_rows)
                  /len(class_rows)) if class_rows else None
        field_metrics=score_records(records) if mode!="classifier_only" else None
        results[mode]={
            "documents":len(entries),"classification_accuracy":accuracy,
            "field_metrics":field_metrics,
            "mean_seconds_per_doc":round(elapsed/len(entries),4),
            "external_api_calls":calls,
            "failed_documents":errors,
        }
    return {"source":"development only, holdout never scored",
            "gemini_enabled":allow_gemini,"modes":results}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset",type=Path,required=True)
    parser.add_argument("--limit",type=int,default=30)
    parser.add_argument("--allow-gemini",action="store_true")
    parser.add_argument("--output",type=Path,default=Path("evaluation/ablation_development.json"))
    args=parser.parse_args()
    result=evaluate(args.dataset,args.limit,args.allow_gemini)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2))
    for name,data in result["modes"].items():
        print(name,{
            "classification_accuracy":data["classification_accuracy"],
            "field_f1":data["field_metrics"]["field_f1"] if data["field_metrics"] else None,
            "external_calls":data["external_api_calls"],"failed":len(data["failed_documents"])
        })
