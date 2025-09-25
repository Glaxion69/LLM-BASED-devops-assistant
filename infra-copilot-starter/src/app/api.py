
from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
from .models import IncidentEvent, Suggestion
from .orchestrator import suggest
from .audit import AuditSink
from ..ingestors.prometheus import from_alertmanager
from ..ingestors.systemd import from_journal_record
from ..ingestors.nginx import from_log_record

# Simple in-memory store for suggestions by id
SUGGESTION_STORE = {}
audit = AuditSink()

router = APIRouter()

@router.post("/ingest/log", response_model=List[Suggestion])
def ingest_log(event: IncidentEvent):
    audit.log_event(event)
    suggestions = suggest(event)
    for s in suggestions:
        SUGGESTION_STORE[str(s.id)] = s
        audit.log_suggestion(s)
    return suggestions

@router.post("/ingest/prometheus", response_model=List[Suggestion])
def ingest_prometheus(payload: dict):
    event = from_alertmanager(payload)
    audit.log_event(event)
    suggestions = suggest(event)
    for s in suggestions:
        SUGGESTION_STORE[str(s.id)] = s
        audit.log_suggestion(s)
    return suggestions

@router.post("/ingest/systemd", response_model=List[Suggestion])
def ingest_systemd(record: dict):
    event = from_journal_record(record)
    audit.log_event(event)
    suggestions = suggest(event)
    for s in suggestions:
        SUGGESTION_STORE[str(s.id)] = s
        audit.log_suggestion(s)
    return suggestions

@router.post("/ingest/nginx", response_model=List[Suggestion])
def ingest_nginx(record: dict):
    event = from_log_record(record)
    audit.log_event(event)
    suggestions = suggest(event)
    for s in suggestions:
        SUGGESTION_STORE[str(s.id)] = s
        audit.log_suggestion(s)
    return suggestions

@router.post("/suggestions/{suggestion_id}/apply")
def apply_suggestion(suggestion_id: str, x_copilot_approval: Optional[str] = Header(default=None, alias="X-Copilot-Approval")):
    if not x_copilot_approval:
        raise HTTPException(status_code=403, detail="approval token required")
    s: Optional[Suggestion] = SUGGESTION_STORE.get(suggestion_id)
    if not s:
        raise HTTPException(status_code=404, detail="suggestion not found")
    # Dry-run: would run these commands
    return {
        "suggestion_id": suggestion_id,
        "approved": True,
        "commands": s.commands,
    }

@router.get("/healthz")
def healthz():
    return {"ok": True}
