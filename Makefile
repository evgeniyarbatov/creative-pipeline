VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip

.PHONY: venv install run-captions test

venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

run-captions:
	$(PYTHON) captions_pipeline.py

test: install
	$(PYTHON) -m pytest -q
