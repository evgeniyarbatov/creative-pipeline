VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

default: run-extract

venv:
	@python3.12 -m venv $(VENV_PATH)

install: venv
	@uv pip install -q -r $(REQUIREMENTS)

run-extract: install
	@$(PYTHON) scripts/extract_pipeline.py
test: install
	@$(PYTHON) -m pytest -q
