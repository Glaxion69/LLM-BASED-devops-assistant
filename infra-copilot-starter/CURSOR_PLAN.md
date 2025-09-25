# Cursor Plan — Infra Copilot (Stage 1 → Stage 3)

## Stage 1 — Orchestrator (LangChain)
- Replace `src/app/orchestrator.py` heuristic with a LangChain pipeline:
  1) Classify source/severity from `IncidentEvent`.
  2) Summarize root cause (<=120 words).
  3) Select a playbook (nginx 502, high CPU, systemd crash).
  4) Generate up to 3 safe commands/diffs with `requires_approval`.
  5) Return `List[Suggestion]`.
- Use `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` from env if present; otherwise fallback to the current heuristic.
- Keep secrets out of code.

## Stage 2 — Parsers & API Routes
- Implement `src/ingestors/prometheus.py` to handle Alertmanager webhooks → `IncidentEvent`.
- Implement `src/ingestors/systemd.py` and `src/ingestors/nginx.py` to normalize raw logs (provided as JSON) → `IncidentEvent`.
- Add routes in `src/app/api.py`:
  - POST /ingest/prometheus
  - POST /ingest/nginx
  - POST /ingest/systemd
- Add unit tests in `tests/` for parsers and endpoints.

## Stage 3 — Slack Bot & Approvals
- Create `src/slack/bot.py` using Slack Bolt (Socket Mode) with `/infra-copilot` command:
  - Open modal to paste logs.
  - Call API POST /ingest/log.
  - Post top suggestion with **Approve** and **Explain** buttons.
- Implement `POST /suggestions/{id}/apply` with an approval check (Slack interaction or signed header).
- Add `src/app/audit.py` to append JSONL lines to `AUDIT_LOG_PATH` for every event and suggestion.

## Stage 4 — CI, Quality, and Packaging
- Add ruff/mypy/pytest to CI in `.github/workflows/ci.yml` (already scaffolded; expand as needed).
- Add Dockerfile for API and Slack worker; optional devcontainer.
- Update README with Slack setup, env vars, and examples.
