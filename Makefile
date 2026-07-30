# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

OLLAMA_MODEL ?= gemma3:latest

default: run

install:
	@uv sync --dev

ollama-pull:
	@ollama pull $(OLLAMA_MODEL)

# Entry point: run the end-to-end extraction pipeline
run: run-extract

run-extract: install ollama-pull
	@uv run python scripts/extract_pipeline.py --model $(OLLAMA_MODEL)

test: install
	@uv run python -m pytest -q

lock:
	@uv lock

clean:
	rm -rf .venv

help:
	@echo "install       - create/update .venv and sync dependencies"
	@echo "ollama-pull   - ensure OLLAMA_MODEL is pulled before run"
	@echo "run           - run the extraction pipeline (entry point)"
	@echo "test          - run tests"
	@echo "lock          - refresh uv.lock"
	@echo "clean         - remove .venv"
