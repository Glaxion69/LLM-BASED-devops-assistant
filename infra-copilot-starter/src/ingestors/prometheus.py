from typing import Dict, Any
from ..app.models import IncidentEvent


def from_alertmanager(payload: Dict[str, Any]) -> IncidentEvent:
    alerts = payload.get("alerts", []) or []
    first = alerts[0] if alerts else {}
    labels = first.get("labels", {}) or {}
    ann = first.get("annotations", {}) or {}
    service = labels.get("service") or labels.get("job")
    node = labels.get("instance")
    summary = ann.get("summary") or labels.get("alertname") or "Prometheus alert"
    details = ann.get("description") or ann.get("message") or ""
    severity = labels.get("severity") or "warning"
    return IncidentEvent(
        source="prometheus",
        severity=severity,
        service=service,
        node=node,
        labels=labels,
        summary=summary,
        details=details,
    )


