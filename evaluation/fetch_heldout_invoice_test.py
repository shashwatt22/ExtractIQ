"""Independently held-out *fictional* invoice test set, not real business data.

Uses the separately authored invoice-agent public benchmark. No examples from
this corpus were used to design the preceding extraction rules.
"""
import json
from pathlib import Path
from urllib.request import Request,urlopen
BASE="https://raw.githubusercontent.com/superintelligenceco/invoice-agent/main/dataset/"
def get(s):
    with urlopen(Request(BASE+s,headers={"User-Agent":"ExtractIQ-heldout/1.0"}),timeout=30) as r:
        return r.read()
def main():
    target=Path("evaluation/heldout_invoices")
    target.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(get("manifest.json"))
    entries=[]
    # Fixed first 20 samples, never selected based on predicted performance.
    for rec in manifest[:20]:
        path=rec["file"]
        name=Path(path).name
        label=json.loads(get("ground_truth/"+name.replace(".pdf",".json")))
        inv=label["invoice"]
        pdf=get(path)
        if not pdf.startswith(b"%PDF"):
            raise ValueError("Invalid PDF "+name)
        (target/name).write_bytes(pdf)
        entries.append({"file":name,"doc_type":"invoice","source_url":BASE+path,
                        "fields":{"invoice_number":str(inv["invoice_number"]),
                                  "total_amount":str(inv["total"])}})
    (target/"manifest.json").write_text(json.dumps(entries,indent=2),encoding="utf-8")
    print("Held-out fictional invoices:",len(entries),"reference fields:",len(entries)*2)
if __name__=="__main__":
    main()
