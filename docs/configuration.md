# Configuration

## Agent and Task Files

Configs live in `agents/` and contain two sections:

- `agent` for persona settings
- `task` for prompts and expected output

Included configs:

- `agents/transcript.yaml` — primary extraction step, produces `memory.json`/`memory.md`.
- `agents/tags.yaml` — legacy, opt-in (produces publish-ready tags; not the project's North Star — see `docs/philosophy.md`).

`agent` supports:

- `role`
- `goal`
- `backstory`
- `allow_delegation`
- `verbose`

`task` supports:

- `description_template`
- `expected_output`

## CLI Options

Run the pipeline directly if you want options beyond `make run-extract`:

```bash
.venv/bin/python scripts/extract_pipeline.py --help
```

Common options:

- `--transcripts-dir /path/to/transcripts`
- `--output-dir /path/to/output`
- `--ollama-base-url http://localhost:11434`
- `--config-dir /path/to/configs`

## Ollama Options

Extraction (`transcript.yaml`) and legacy derivation (`tags.yaml`) use different option sets, since transcripts are long and extraction should not truncate:

Extraction:

- `temperature: 0.7`
- `top_p: 0.9`
- `repeat_penalty: 1.1`
- `num_predict: 1024`

Derivation (tags):

- `temperature: 0.4`
- `top_p: 0.85`
- `repeat_penalty: 1.15`
- `num_predict: 120`
