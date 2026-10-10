"""Fetch a small public invoice2data fixture subset for a reproducible external-PDF evaluation.

The fixture metadata are upstream expected values, not independently audited
manual annotations. Do not claim this is an unbiased production benchmark.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://raw.githubusercontent.com/invoice-x/invoice2data/master/tests/compare/"
NAMES = [
    "AmazonWebServices",
    "QualityHosting",
    "FlipkartInvoice",
    "AzureInterior",
    "NetpresseInvoice",
    "SammyMaystoneLinesTest",
    "coolblue1",
    "coolblue2",
    "free_fiber",
    "oyo",
    "saeco",
]
FIELDS = {"invoice_number": "invoice_number", "amount": "total_amount"}

def download(name, suffix):
    url=BASE+name+suffix
    req=Request(url,headers={"User-Agent":"ExtractIQ-benchmark/1.0"})
    with urlopen(req,timeout=30) as resp:
        return resp.read()

def main():
    root=Path("evaluation/external_invoices")
    root.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name in NAMES:
        try:
            raw=download(name,".json")
            reference=json.loads(raw)
            if not isinstance(reference,list) or not reference:
                print("SKIP",name,"empty reference")
                continue
            record=reference[0]
            fields={}
            for upstream,ours in FIELDS.items():
                if record.get(upstream) is not None:
                    fields[ours]=str(record[upstream])
            if len(fields)<2:
                print("SKIP",name,"not enough common fields")
                continue
            pdf=download(name,".pdf")
            if not pdf.startswith(b"%PDF"):
                print("SKIP",name,"not a PDF")
                continue
            (root/(name+".pdf")).write_bytes(pdf)
            manifest.append({"file":name+".pdf","source_url":BASE+name+".pdf",
                             "doc_type":"invoice","fields":fields})
        except Exception as e:
            print("SKIP",name,type(e).__name__,str(e)[:80])
    if len(manifest)<5:
        raise RuntimeError(f"Only {len(manifest)} reference PDFs available")
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print("Downloaded",len(manifest),"public PDFs; evaluated fields: invoice number and total amount")

if __name__=="__main__":
    main()
