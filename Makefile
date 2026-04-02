VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

default: run-captions

venv:
	@python3.12 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

run-captions:
	@$(PYTHON) scripts/captions_pipeline.py

test:
	@$(PYTHON) -m pytest -q
