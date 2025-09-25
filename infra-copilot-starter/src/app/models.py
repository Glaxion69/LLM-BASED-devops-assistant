
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class IncidentEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    ts: datetime = Field(default_factory=datetime.utcnow)
    source: str  # "prometheus" | "systemd" | "nginx" | "custom"
    severity: str = "info"  # "info" | "warning" | "critical"
    service: Optional[str] = None
    node: Optional[str] = None
    labels: Dict[str, str] = {}
    summary: str
    details: str

class Suggestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    confidence: float = 0.6
    title: str
    rationale: str
    commands: List[str] = []
    diffs: List[str] = []
    requires_approval: bool = True
