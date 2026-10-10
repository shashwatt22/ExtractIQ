"""Conservative multilingual invoice-field fallbacks.

These are general label patterns, not vendor-specific templates. The patterns
are used only if the primary invoice rule did not extract a value.
"""
from __future__ import annotations
import re
from .base import ExtractedField

NUMBER_LABELS = (
    r"invoice\s*(?:no\.?|number|#|nr\.?|id)",
    r"(?:facture|rechnung|factuur|fattura)\s*(?:n[°o.]|nr\.?|number|no\.?)",
    r"(?:invoice|bill|tax invoice)\s*#",
    r"(?:bill|receipt)\s*(?:number|no\.?|#|id)",
)
AMOUNT_LABELS = (
    r"(?:grand\s+total|total\s+(?:amount|due|payable|incl\.?\s*tax|inc\.?\s*vat))",
    r"(?:amount\s+(?:due|payable)|balance\s+due|net\s+to\s+pay)",
    r"(?:montant\s+(?:total|ttc)|total\s+ttc|gesamtbetrag|rechnungsbetrag|totaal\s+(?:incl|te\s+betalen))",
)
NUMERIC = r"(?:[$€£₹]|USD|EUR|GBP|INR)?\s*\d[\d., ]{0,20}(?:[$€£₹])?"
INVOICE_REF = r"[#A-Za-z0-9][A-Za-z0-9_/#.\-]{3,45}"

def normalize_amount(raw: str) -> str:
    value=raw.strip()
    # No generic guessing for ambiguous 1,234 formats.
    value=re.sub(r"\s+","",value)
    return value

def supplemental_invoice_fields(text: str, existing_names: set[str]) -> list[ExtractedField]:
    additions=[]
    if "invoice_number" not in existing_names:
        for label in NUMBER_LABELS:
            pattern=rf"(?im)\b(?:{label})\s*[:#=\-]?\s*({INVOICE_REF})"
            match=re.search(pattern,text)
            if match:
                value=match.group(1).strip()
                if re.search(r"\d",value) and value.lower() not in {"date","total","amount"}:
                    additions.append(ExtractedField("invoice_number",value,0.70,"rules"))
                    break
    if "total_amount" not in existing_names:
        for label in AMOUNT_LABELS:
            match=re.search(rf"(?im)(?:{label})\s*[:=\-]?\s*({NUMERIC})",text)
            if match and re.search(r"\d",match.group(1)):
                additions.append(ExtractedField("total_amount",normalize_amount(match.group(1)),0.66,"rules"))
                break
    return additions
