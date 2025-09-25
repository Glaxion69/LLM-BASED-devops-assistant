
from typing import List
from .models import IncidentEvent, Suggestion

# MVP heuristic stub; replace with LangChain via Cursor
def suggest(event: IncidentEvent) -> List[Suggestion]:
    base = {
        "event_id": event.id,
        "title": "Review service and restart gracefully",
        "rationale": f"Source={event.source}, severity={event.severity}. Start with safe checks.",
        "commands": [
            "sudo systemctl status " + (event.service or "SERVICE"),
            "sudo journalctl -u " + (event.service or "SERVICE") + " -n 200",
            "sudo systemctl restart " + (event.service or "SERVICE") + " --no-block",
        ],
        "diffs": [],
        "requires_approval": True,
    }
    if event.source == "nginx":
        base["title"] = "Inspect upstream timeouts and reload Nginx"
        base["commands"] = [
            "sudo tail -n 200 /var/log/nginx/error.log",
            "sudo nginx -t",
            "sudo systemctl reload nginx",
        ]
    return [Suggestion(**base)]
