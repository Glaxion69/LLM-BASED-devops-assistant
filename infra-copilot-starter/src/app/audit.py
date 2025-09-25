import os
import json
from datetime import datetime
from typing import Any, Dict, Optional


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class AuditSink:
    """Append JSON lines to a configured file for auditability.

    Path comes from AUDIT_LOG_PATH; defaults to results/audit.jsonl.
    Ensures parent directories exist. Failures are swallowed to avoid impacting API.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.getenv("AUDIT_LOG_PATH", "results/audit.jsonl")
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        except Exception:
            # Ignore directory creation errors to avoid blocking
            pass

    def write(self, record: Dict[str, Any]) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                line = json.dumps(record, ensure_ascii=False)
                f.write(line + "\n")
        except Exception:
            # Swallow file errors in audit sink
            pass

    def log_event(self, event: Any) -> None:
        try:
            self.write({
                "ts": _now_iso(),
                "type": "incident_event",
                "event": json.loads(event.model_dump_json()),
            })
        except Exception:
            pass

    def log_suggestion(self, suggestion: Any) -> None:
        try:
            self.write({
                "ts": _now_iso(),
                "type": "suggestion",
                "suggestion": json.loads(suggestion.model_dump_json()),
            })
        except Exception:
            pass


