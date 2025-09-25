# Infra Copilot

LLM-powered DevOps copilot (API + CLI + Slack) for log/alert remediation.

## Quick start
```bash
python -m venv .venv
# Windows: . .venv/Scripts/activate
# macOS/Linux: source .venv/bin/activate
pip install -e .[dev]
uvicorn src.app.main:app --reload --port 8000
# open http://127.0.0.1:8000/docs
```

## CLI
```bash
python -m src.cli.main suggest '{"source":"nginx","summary":"502s","details":"upstream timeout","service":"nginx"}'
```

## Environment
- OPENAI_API_KEY, ANTHROPIC_API_KEY (optional)
- SLACK_BOT_TOKEN, SLACK_APP_TOKEN (for Socket Mode)
- AUDIT_LOG_PATH (default results/audit.jsonl)
- PORT (default 8000)

No secrets are hardcoded. If no AI keys are set, the orchestrator falls back to a heuristic.

## API
- POST `/ingest/log` — `IncidentEvent`
- POST `/ingest/prometheus` — Alertmanager JSON
- POST `/ingest/systemd` — journal record JSON
- POST `/ingest/nginx` — nginx log record JSON
- POST `/suggestions/{id}/apply` — requires `X-Copilot-Approval`; dry-run commands

## Slack (Socket Mode)
```bash
python scripts/run_slack.py
```
Use `/infra-copilot` to open a modal.

## Docker
```bash
docker compose up --build
```
