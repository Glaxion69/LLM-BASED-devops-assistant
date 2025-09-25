
import json
import typer
from pydantic import ValidationError
from src.app.models import IncidentEvent
from src.app.orchestrator import suggest

app = typer.Typer(help="Infra Copilot CLI")

@app.command()
def ingest(event_json: str):
    """
    Pass a JSON string of IncidentEvent; returns suggestions JSON.
    Example:
      copilot ingest '{"source":"nginx","summary":"502s","details":"..."}'
    """
    try:
        data = json.loads(event_json)
        evt = IncidentEvent(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        typer.echo(f"Invalid event JSON: {e}")
        raise typer.Exit(code=2)
    for s in suggest(evt):
        typer.echo(json.dumps(s.model_dump(), default=str))

if __name__ == "__main__":
    app()
