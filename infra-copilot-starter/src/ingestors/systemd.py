from typing import Dict, Any
from ..app.models import IncidentEvent


def from_journal_record(record: Dict[str, Any]) -> IncidentEvent:
    unit = record.get("_SYSTEMD_UNIT") or record.get("UNIT")
    ident = record.get("SYSLOG_IDENTIFIER")
    service = unit.split(".")[0] if isinstance(unit, str) and "." in unit else unit
    message = record.get("MESSAGE") or "systemd event"
    severity_map = {"0": "critical", "1": "critical", "2": "critical", "3": "warning"}
    priority = str(record.get("PRIORITY") or "5")
    severity = severity_map.get(priority, "info")
    return IncidentEvent(
        source="systemd",
        severity=severity,
        service=service or ident,
        node=record.get("_HOSTNAME"),
        labels={k: str(v) for k, v in record.items() if isinstance(k, str)},
        summary=f"systemd: {message[:80]}",
        details=message,
    )


