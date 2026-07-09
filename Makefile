# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

default: run-extract

install:
	@uv sync --dev

run-extract: install
	@uv run python scripts/extract_pipeline.py

test: install
	@uv run python -m pytest -q

lock:
	@uv lock

clean:
	rm -rf .venv

help:
	@echo "install       - create/update .venv and sync dependencies"
	@echo "run-extract   - run the extraction pipeline"
	@echo "test          - run tests"
	@echo "lock          - refresh uv.lock"
	@echo "clean         - remove .venv"
