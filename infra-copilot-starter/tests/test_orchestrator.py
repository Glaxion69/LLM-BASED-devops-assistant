import os
from src.app.models import IncidentEvent
from src.app.orchestrator import suggest


def test_orchestrator_fallback_without_keys(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    evt = IncidentEvent(source="nginx", summary="502 Bad Gateway", details="connect() timed out", service="nginx")
    suggestions = suggest(evt)
    assert isinstance(suggestions, list)
    assert len(suggestions) >= 1
    s = suggestions[0]
    assert s.requires_approval is True
    assert isinstance(s.commands, list)


