# creative-pipeline

Extracts structured artist memory (threads, contradictions, tangents, open questions, anchor quotes) from raw transcripts, using CrewAI agents backed by a local Ollama model. Not captions or marketing copy — see `docs/philosophy.md`.

## Entry points

- `scripts/extract_pipeline.py` — the pipeline itself: loads a transcript, runs the CrewAI agents/tasks, writes `memory.json` / `memory.md` / `tags.txt`.
- `agents/tags.yaml`, `agents/transcript.yaml` — CrewAI agent/task definitions.
- `scripts/agent_config.py`, `scripts/task_config.py` — load and validate the YAML configs above.
- `scripts/memory_schema.py` — parses/validates the model's memory output, renders the markdown mirror.
- `scripts/pipeline_utils.py` — shared helpers (e.g. artwork name derivation, tag normalization).

## How to run

```bash
make run
```

Requires Ollama installed and running; `make run` pulls `OLLAMA_MODEL` (default `gemma3:latest`) first, then runs the pipeline via `uv run`. Input transcripts default to `~/Documents/art-talks/*.txt` (outside the repo); see `docs/getting-started.md`.

## Conventions / gotchas

- Dependency management is `uv` — no manual venv activation, everything runs via `uv run`.
- Transcripts and generated outputs live outside the repo (`~/Documents/art-talks/`), not under `examples/`.
- `tags.txt` generation is a legacy, opt-in-by-default derivation — see `docs/configuration.md` before changing its default.
- Tests: `make test` (pytest, offline, no Ollama required for most of the suite except where a test explicitly exercises Ollama options).
