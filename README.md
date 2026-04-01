# Creative Pipeline: Social Caption Generator

This pipeline generates platform-specific social captions from your transcript files using CrewAI + Ollama (`phi3:mini`).

## What It Does

For each transcript in `~/Documents/art-talks/*.txt`, the pipeline creates:

- `~/Documents/art-talks/<artwork-name>/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/tags.txt` (shared tags for all platforms)

The captions share a common voice agent and then adapt to each platform's style rules.

## Prerequisites

1. Install and run Ollama.
2. Pull the model:

```bash
ollama pull phi3:mini
```

3. Create the virtual environment and install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Or use the Makefile (recommended):

```bash
make install
```

## Run The Pipeline

```bash
python scripts/captions_pipeline.py --transcripts-dir ~/Documents/art-talks
```

Or use the Makefile:

```bash
make run-captions
```

Optional flags:

- `--platforms facebook instagram` (generate a subset)
- `--output-dir /path/to/output` (defaults to the transcript dir)
- `--dry-run` (inspect output paths without calling the model)
- `--ollama-base-url http://localhost:11434`
- `--agents-dir /path/to/agents` (directory of per-agent YAML configs)
- `--tasks-dir /path/to/tasks` (directory of per-task YAML configs)

## Adding Extra Context (Extensible Design)

You can attach extra context per artwork and the pipeline will include it automatically. Place one of these files next to the transcript or inside a `context/` folder:

- `~/Documents/art-talks/<artwork>.context.txt`
- `~/Documents/art-talks/<artwork>.context.md`
- `~/Documents/art-talks/context/<artwork>.txt`
- `~/Documents/art-talks/context/<artwork>.md`
- `~/Documents/art-talks/context/<artwork>.json`

This is meant for future expansion (image notes, intended audience, links, etc.).

## Extending Platforms

To add a new platform:

1. Add a new agent YAML file in `config/agents/<platform>.yaml`.
2. Add a new task YAML file in `config/tasks/<platform>.yaml`.
3. Pass the new platform name via `--platforms` or add it to `DEFAULT_PLATFORMS` in `scripts/pipeline_utils.py`.

## Agent Configuration

Each agent is configured in its own YAML file under `config/agents/`:

- `config/agents/voice.yaml`
- `config/agents/personality.yaml`
- `config/agents/tags.yaml`
- `config/agents/facebook.yaml`
- `config/agents/instagram.yaml`
- `config/agents/deviantart.yaml`
- `config/agents/pinterest.yaml`

Each file supports these keys:

- `role`
- `goal`
- `backstory`
- `allow_delegation`
- `verbose`

## Task Configuration

Each task is configured in its own YAML file under `config/tasks/`:

- `config/tasks/voice.yaml`
- `config/tasks/personality.yaml`
- `config/tasks/tags.yaml`
- `config/tasks/facebook.yaml`
- `config/tasks/instagram.yaml`
- `config/tasks/deviantart.yaml`
- `config/tasks/pinterest.yaml`

Each file supports these keys:

- `description_template`
- `expected_output`
- `display_name` (platform tasks only)
- `style_rules` (platform tasks only)
- `output_rules` (platform tasks only)

## Tests

```bash
make test
```

Tests focus on path and context discovery logic so you can change copy rules without breaking IO.
