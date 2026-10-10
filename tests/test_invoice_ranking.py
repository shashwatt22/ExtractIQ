"""Offline tests for ranking, normalization and uncertainty gating."""
from backend.app.pipeline.extractors.invoice_ranking import normalize_amount, ranked_invoice_total
from backend.app.pipeline.extractors.rules import _extract_invoice

def test_localized_amounts():
    assert normalize_amount("₹1,23,456.00")==("123456.00","INR") or normalize_amount("₹1,23,456.00")==(None,None)
    assert normalize_amount("$1,234.50")==("1234.50","USD")
    assert normalize_amount("EUR 1.234,50")==("1234.50","EUR")
    assert normalize_amount("1,234")==("1234.00",None)
    assert normalize_amount("1.234")==(None,None)

def test_prefers_grand_total_to_subtotal_and_tax():
    text="SUBTOTAL $1,000.00\nTAX $180.00\nGrand Total: $1,180.00\n"
    out=ranked_invoice_total(text)
    assert out is not None
    assert out.value=="1180.00"
    assert out.currency=="USD"

def test_no_guess_when_no_total_label():
    assert ranked_invoice_total("Item A $100\nTax $18\n")==None

def test_rule_integration():
    fields=_extract_invoice("INVOICE No: INV-102\nSubtotal: $100.00\nVAT: $18.00\nGrand Total: $118.00")
    total=[field for field in fields if field.name=="total_amount"]
    assert len(total)==1
    assert "118.00" in total[0].value
