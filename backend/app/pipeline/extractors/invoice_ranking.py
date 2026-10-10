"""Conservative invoice candidate ranking and cross-currency normalization.

Never converts currencies. Does not resolve ambiguous number formats by guessing.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

MONEY = re.compile(r"(?<!\w)(?P<currency>INR|USD|EUR|GBP|₹|\$|€|£)?\s*(?P<number>\d[\d., ]{0,18}\d|\d)(?!\w)", re.I)
GOOD = re.compile(r"\b(grand\s+total|total\s+(?:amount|due|payable)|amount\s+due|balance\s+due|net\s+payable|invoice\s+total|total\s+incl(?:uding)?\s+(?:vat|tax))\b", re.I)
GENERIC = re.compile(r"(?<!sub)\btotal\b", re.I)
BAD = re.compile(r"\b(subtotal|sub\s+total|tax|vat|gst|unit\s+price|discount|shipping|line\s+total|amount\s+paid)\b", re.I)
CURRENCY={"₹":"INR","$":"USD","€":"EUR","£":"GBP"}

def normalize_amount(value: str) -> tuple[str | None, str | None]:
    raw=value.strip()
    m=re.fullmatch(r"\s*(INR|USD|EUR|GBP|₹|\$|€|£)?\s*(\d[\d., ]*)\s*",raw,re.I)
    if not m:
        return None,None
    currency=m.group(1)
    number=m.group(2).replace(" ","")
    if "," in number and "." in number:
        dec="," if number.rfind(",")>number.rfind(".") else "."
        thousands="." if dec=="," else ","
        number=number.replace(thousands,"").replace(dec,".")
    elif "," in number:
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+",number):
            number=number.replace(",","")
        elif re.fullmatch(r"\d+,\d{2}",number):
            number=number.replace(",",".")
        else:
            return None,None
    elif "." in number:
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+",number):
            return None,None  # 1.234 could be decimal or thousand-separated
        if number.count(".")>1:
            return None,None
    try:
        amount=Decimal(number)
    except InvalidOperation:
        return None,None
    if not amount.is_finite() or amount < 0:
        return None,None
    normalized=str(amount.quantize(Decimal("0.01")))
    return normalized,CURRENCY.get(currency,currency.upper() if currency else None)

@dataclass(frozen=True)
class RankedAmount:
    value: str
    currency: str | None
    confidence: float
    line: str
    index: int

def ranked_invoice_total(text: str) -> RankedAmount | None:
    candidates=[]
    for index,line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        good=GOOD.search(line)
        generic=GENERIC.search(line)
        if not good and not generic:
            continue
        if BAD.search(line) and not good:
            continue
        label=good or generic
        tail=line[label.end():]
        for match in MONEY.finditer(tail):
            amount,currency=normalize_amount(match.group(0))
            if amount is None:
                continue
            # Reject invoice dates, unit prices and percentages.
            if "%" in tail[max(0,match.start()-3):match.end()+2]:
                continue
            distance=match.start()
            conf=(0.90 if good else 0.66)-min(0.30,distance*0.008)
            if BAD.search(line[:label.start()]):
                conf-=0.20
            if currency:
                conf+=0.03
            candidates.append(RankedAmount(amount,currency,round(min(conf,0.96),3),line,index))
    if not candidates:
        return None
    result=max(candidates,key=lambda c:(c.confidence,c.index))
    return result if result.confidence>=0.60 else None
