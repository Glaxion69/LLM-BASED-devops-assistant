# Infra Copilot (Starter)

LLM‑powered DevOps assistant (API + CLI + Slack). This starter runs a minimal API + CLI with heuristic suggestions. Use Cursor to extend it with LangChain, Slack bot, and parsers.

## Quick start
```bash
python -m venv .venv
# Windows: . .venv/Scripts/activate
# macOS/Linux: source .venv/bin/activate
pip install -e .[dev]
make run
# open http://127.0.0.1:8000/docs
```

## Try the CLI
```bash
python -m src.cli.main ingest '{"source":"nginx","summary":"502s","details":"upstream timeout","service":"nginx"}'
```

## Next with Cursor (see CURSOR_PLAN.md)
- Replace orchestrator with LangChain
- Add Slack bot (Bolt) + approvals
- Add Prometheus/systemd/Nginx parsers
