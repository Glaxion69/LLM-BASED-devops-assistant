from typing import Dict, Any
from ..app.models import IncidentEvent


def from_log_record(record: Dict[str, Any]) -> IncidentEvent:
    status = record.get("status")
    upstream_status = record.get("upstream_status")
    service = "nginx"
    summary = f"Nginx {status} on request" if status else "Nginx log"
    details = (
        f"request={record.get('request')} upstream_status={upstream_status} request_time={record.get('request_time')}"
    )
    severity = "warning" if status and int(status) >= 500 else "info"
    return IncidentEvent(
        source="nginx",
        severity=severity,
        service=service,
        node=None,
        labels={k: str(v) for k, v in record.items()},
        summary=summary,
        details=details,
    )


