"""External RAG provider must never receive unconsented unmasked text."""
from types import SimpleNamespace
import sys
from unittest.mock import MagicMock

from backend.app.rag import qa

def test_rag_blocks_external_without_consent(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY","fake")
    client=MagicMock()
    monkeypatch.setitem(sys.modules,"anthropic",SimpleNamespace(Anthropic=lambda **k:client))
    hits=[{"meta":{"filename":"patient-alice.pdf","page":1},
           "text":"Patient Name: Alice Example\nEmail jane@example.org\nAddress: 12 Main Street"}]
    assert qa._llm_answer("Who is Alice?",hits,consent=False) is None
    client.messages.create.assert_not_called()

def test_rag_masks_context_question_and_filename(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY","fake")
    client=MagicMock()
    client.messages.create.return_value.content=[SimpleNamespace(type="text",text="masked answer")]
    monkeypatch.setitem(sys.modules,"anthropic",SimpleNamespace(Anthropic=lambda **k:client))
    hits=[{"meta":{"filename":"alice-private.pdf","page":1},
           "text":"Patient Name: Alice Example\nEmail: jane@example.org\nAddress: 12 Main Street"}]
    result=qa._llm_answer("Contact jane@example.org",hits,consent=True)
    assert result=="masked answer"
    request=client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "Alice Example" not in request
    assert "jane@example.org" not in request
    assert "12 Main Street" not in request
    assert "alice-private.pdf" not in request
