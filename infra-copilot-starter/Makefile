
    .PHONY: init run api cli test fmt

    init:
	python -m venv .venv && . .venv/Scripts/activate || . .venv/bin/activate; \
	pip install -e .[dev]

    run:
	uvicorn src.app.main:app --reload --port $${PORT:-8000}

    api:
	python -c "import webbrowser; webbrowser.open('http://127.0.0.1:8000/docs')"

    cli:
	python -m src.cli.main --help

    test:
	pytest -q

    fmt:
	ruff check --select I --fix . ; ruff check .
