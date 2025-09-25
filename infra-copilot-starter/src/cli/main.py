
import os
import json
from pathlib import Path
import typer
import requests
from pydantic import ValidationError
from src.app.models import IncidentEvent

app = typer.Typer(help="Infra Copilot CLI")

def _api_url() -> str:
    port = int(os.getenv("PORT", "8000"))
    return f"http://127.0.0.1:{port}"

@app.command()
def ingest_file(file: Path, service: str = typer.Option(None), source: str = "custom"):
    """Read a file and send as IncidentEvent to /ingest/log."""
    try:
        text = file.read_text(encoding="utf-8")
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}))
        raise typer.Exit(code=1)
    evt = IncidentEvent(source=source, summary=text[:100], details=text, service=service)
    r = requests.post(f"{_api_url()}/ingest/log", json=json.loads(evt.model_dump_json()))
    typer.echo(json.dumps(r.json()))

@app.command()
def suggest(json_event: str):
    """Send IncidentEvent JSON to /ingest/log and print suggestions."""
    try:
        data = json.loads(json_event)
    except json.JSONDecodeError as e:
        typer.echo(json.dumps({"error": f"invalid json: {e}"}))
        raise typer.Exit(code=2)
    r = requests.post(f"{_api_url()}/ingest/log", json=data)
    typer.echo(json.dumps(r.json()))

@app.command()
def apply(id: str, approve_token: str):
    """Approve a suggestion (dry-run) and print commands that would run."""
    headers = {"X-Copilot-Approval": approve_token}
    r = requests.post(f"{_api_url()}/suggestions/{id}/apply", headers=headers)
    typer.echo(json.dumps(r.json()))

if __name__ == "__main__":
    app()
