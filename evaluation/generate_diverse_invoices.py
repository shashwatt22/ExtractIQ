"""Generate 180 deterministic, diverse FICTIONAL invoices.

Development = first 150; sealed holdout = last 30. Never inspect holdout
results while developing rules. This is not a substitute for public real invoices.
"""
from __future__ import annotations
import argparse
from datetime import date, timedelta
from io import BytesIO
import json
from pathlib import Path
import random
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen.canvas import Canvas

CURRENCIES=[("USD","$"),("EUR","€"),("INR","₹")]
LABELS=[
    ("Invoice No:", "Grand Total:"),
    ("Invoice Number:", "Total Amount Due:"),
    ("Invoice #", "Amount Due:"),
    ("Bill Number:", "Balance Due:"),
    ("Tax Invoice No:", "Total Payable:"),
]
FONTS=["Helvetica","Helvetica-Bold","Times-Roman","Courier"]
SOURCE_TAG="generated-synthetic-fixture"

def make_all(output:Path, count:int=180)->None:
    if count!=180:
        raise ValueError("Fixture partition is intentionally fixed at 180")
    rng=random.Random(281827)
    for segment in ("development","sealed_holdout"):
        (output/segment).mkdir(parents=True,exist_ok=True)
    manifest={"development":[],"sealed_holdout":[]}
    for i in range(count):
        split="development" if i<150 else "sealed_holdout"
        invoice_number=f"SI-{i+1:05d}"
        currency_code,symbol=CURRENCIES[i%len(CURRENCIES)]
        subtotal=round(rng.uniform(120,7000),2)
        tax=round(subtotal*([.0,.05,.09,.18][i%4]),2)
        shipping=round([0,0,15.5,35][i%4],2)
        total=round(subtotal+tax+shipping,2)
        invoice_label,total_label=LABELS[i%len(LABELS)]
        if i%4==0:
            amount=lambda v:f"{v:,.2f}"
        elif i%4==1:
            amount=lambda v:f"{v:.2f}"
        elif i%4==2:
            amount=lambda v:f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        else:
            amount=lambda v:f"{v:,.2f}"
        # ReportLab built-ins do not render many Unicode currency glyphs.
        printable=symbol if symbol=="$" else currency_code
        number=f"{printable} {amount(total)}"
        name=f"fixture_{i+1:04d}.pdf"
        path=output/split/name
        p=Canvas(str(path),pagesize=A4 if i%2 else letter)
        p.setTitle("FICTIONAL invoice evaluation fixture")
        p.setFont(FONTS[i%len(FONTS)],11)
        header=[f"INVOICE {i+1:03d}",f"INVOICE / TAX",f"BILLING DETAILS"][i%3]
        p.drawString(45,770,header)
        p.drawString(45,736,f"{invoice_label} {invoice_number}")
        d=date(2024,1,1)+timedelta(days=i*2)
        date_value=[d.strftime("%d/%m/%Y"),d.strftime("%Y-%m-%d"),d.strftime("%b %d, %Y")][i%3]
        p.drawString(45,710,f"Invoice Date: {date_value}")
        p.drawString(45,681,"Supplier: Sample Vendor Limited")
        p.drawString(45,657,"Customer: Test Buyer Co")
        start=590 if i%3 else 530
        x=45 if i%2 else 250
        p.drawString(x,start,f"Subtotal: {printable} {amount(subtotal)}")
        p.drawString(x,start-24,f"Tax / VAT: {printable} {amount(tax)}")
        p.drawString(x,start-48,f"Shipping: {printable} {amount(shipping)}")
        # Vary label placement without separating it from value.
        p.drawString(x,start-95,f"{total_label} {number}")
        if i%9==0:
            p.showPage()
            p.setFont("Helvetica",10)
            p.drawString(45,750,"Itemization continued. Total on the preceding page.")
            p.drawString(45,720,"Additional product terms and disclosures.")
        p.save()
        if i % 12 == 0:
            # Convert a subset to image-only PDFs to exercise the real OCR path.
            # Rendering and reconstruction preserve every page of multi-page PDFs.
            import pypdfium2 as pdfium
            from reportlab.lib.utils import ImageReader
            original=pdfium.PdfDocument(str(path))
            images=[original[j].render(scale=1.5).to_pil().convert("RGB")
                    for j in range(len(original))]
            original.close()
            raster=Canvas(str(path),pagesize=(612,792))
            for image in images:
                raster.setPageSize((612,792))
                raster.drawImage(ImageReader(image),0,0,width=612,height=792)
                raster.showPage()
            raster.save()
        manifest[split].append({
            "file":name,"doc_type":"invoice",
            "source_url":f"{SOURCE_TAG}:{name}",
            "fields":{"invoice_number":invoice_number,"total_amount":number},
            "synthetic":True,"currency":currency_code, "scanned_fixture":i%12==0
        })
    for segment in manifest:
        (output/segment/"manifest.json").write_text(json.dumps(manifest[segment],indent=2))
    print("Generated:",{k:len(v) for k,v in manifest.items()})
    print("The sealed_holdout partition must not be scored during development.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("evaluation/diverse_synthetic"))
    args=parser.parse_args()
    make_all(args.output)
