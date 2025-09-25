
from fastapi import APIRouter
from typing import List
from .models import IncidentEvent, Suggestion
from .orchestrator import suggest

router = APIRouter()

@router.post("/ingest/log", response_model=List[Suggestion])
def ingest_log(event: IncidentEvent):
    return suggest(event)

@router.get("/healthz")
def healthz():
    return {"ok": True}
