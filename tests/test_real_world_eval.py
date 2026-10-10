"""Check strict field metric behavior without downloading datasets."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluation.real_world_eval import score_records

def test_exact_matching_and_normalization():
    got=score_records([{"truth":{"total":"$1,200.00","date":"2026-10-10"},"predicted":{"total":"1200.00","date":"2026-10-11"}}])
    assert got["correct"]==1 and got["wrong"]==1 and got["missed"]==1
    assert got["field_f1"]==0.5

def test_missing():
    got=score_records([{"truth":{"invoice_number":"123"},"predicted":{}}])
    assert got["field_recall"]==0.0
