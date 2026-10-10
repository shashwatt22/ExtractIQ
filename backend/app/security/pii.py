"""Conservative default identifier masking before external model calls."""
from __future__ import annotations
import re

def redact_basic_pii(document_text: str) -> str:
    """Best-effort default masking before external processing.

    Covers common structured identifiers and labeled names/addresses, but cannot
    guarantee removal of every name, address, document ID, or medical identifier.
    Clinical/confidential documents must not be submitted to this demo.
    """
    masked = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[REDACTED_EMAIL]", document_text,
    )
    masked = re.sub(
        r"(?<![A-Za-z0-9])(?:\+?\d[\d() .-]{8,}\d)(?![A-Za-z0-9])",
        "[REDACTED_NUMBER]", masked,
    )
    # National ID forms (partial, deliberately conservative).
    masked = re.sub(r"(?i)\b[A-Z]{5}\d{4}[A-Z]\b", "[REDACTED_ID]", masked)
    masked = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_ID]", masked)
    masked = re.sub(
        r"(?im)^(\s*(?:patient|client|customer|contact|full)\s+name\s*[:=\-])\s*([^\r\n]+)",
        r"\1 [REDACTED_NAME]", masked,
    )
    masked = re.sub(
        r"(?im)^(\s*(?:billing|shipping|residential|mailing)?\s*address\s*[:=\-])\s*([^\r\n]+)",
        r"\1 [REDACTED_ADDRESS]", masked,
    )
    masked = re.sub(
        r"(?im)^(\s*(?:patient|member|policy|passport|account|customer)\s*(?:id|no\.?|number)\s*[:=\-])\s*([^\r\n]+)",
        r"\1 [REDACTED_ID]", masked,
    )
    return masked
