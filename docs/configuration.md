# Configuration

## Agent and Task Files

Configs live in `agents/` and contain two sections:

- `agent` for persona settings
- `task` for prompts and expected output

Included configs:

- `agents/transcript.yaml` — primary extraction step, produces `memory.json`/`memory.md`.

Legacy, opt-in (produce publish-ready text; not the project's North Star — see `docs/philosophy.md`):

- `agents/tags.yaml`
- `agents/facebook.yaml`
- `agents/instagram.yaml`
- `agents/deviantart.yaml`
- `agents/pinterest.yaml`

`agent` supports:

- `role`
- `goal`
- `backstory`
- `allow_delegation`
- `verbose`

`task` supports:

- `description_template`
- `expected_output`
- `display_name` (platform tasks only)
- `style_rules` (platform tasks only)
- `output_rules` (platform tasks only)

## CLI Options

Run the pipeline directly if you want options beyond `make run-extract`:

```bash
.venv/bin/python scripts/extract_pipeline.py --help
```

Common options:

- `--platforms facebook instagram`
- `--transcripts-dir /path/to/transcripts`
- `--output-dir /path/to/output`
- `--ollama-base-url http://localhost:11434`
- `--config-dir /path/to/configs`

## Ollama Options

Extraction (`transcript.yaml`) and legacy derivations (`tags.yaml`, platform configs) use different option sets, since transcripts are long and extraction should not truncate:

Extraction:

- `temperature: 0.7`
- `top_p: 0.9`
- `repeat_penalty: 1.1`
- `num_predict: 1024`

Derivation (tags, platform captions):

- `temperature: 0.4`
- `top_p: 0.85`
- `repeat_penalty: 1.15`
- `num_predict: 120`

## Add a New Platform

1. Add `agents/<platform>.yaml` with both `agent` and `task` sections.
2. Run with `--platforms <platform>` or omit `--platforms` to auto-detect configs.
