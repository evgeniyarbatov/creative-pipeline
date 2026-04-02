# Creative Pipeline: Social Caption Generator

This pipeline generates platform-specific social captions from your transcript files using CrewAI + Ollama (`gemma3:latest`).

## What It Does

For each transcript in `~/Documents/art-talks/*.txt`, the pipeline creates:

- `~/Documents/art-talks/<artwork-name>/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/tags.txt` (shared tags for all platforms)
- `~/Documents/art-talks/<artwork-name>/transcript_analysis.txt` (structured extraction used downstream)

The captions share a common transcript analysis agent, adapt to each platform's style rules, and then
run through a personality styling pass before final output.

## High-Level Design

The pipeline is intentionally split into configuration and execution:

- Unified configs live in `agents/*.yaml` with both `agent` and `task` sections.
- Each file defines the agent persona plus the prompt template and expected output.
- The runtime (in `scripts/captions_pipeline.py`) wires agents + tasks together using CrewAI.

For each transcript, the execution flow is:

1. Load the transcript text.
2. Analyze transcript and extract using `agents/transcript.yaml`.
3. Run the tags task to generate reusable tags.
4. Run each platform task to produce a base caption using the analyzed transcript as input.
5. Run the personality styling task to rewrite each platform caption.

Outputs are written into `~/Documents/art-talks/<artwork-name>/` with one file per platform plus `tags.txt` and `transcript_analysis.txt`.

## Prerequisites

1. Install and run Ollama.
2. Pull the model:

```bash
ollama pull gemma3:latest
```

3. Create the virtual environment and install dependencies:

```bash
make install
```

## Run The Pipeline

```bash
make run-captions
```

Optional flags:

- `--platforms facebook instagram` (generate a subset)
- `--output-dir /path/to/output` (defaults to the transcript dir)
- `--dry-run` (inspect output paths without calling the model)
- `--ollama-base-url http://localhost:11434`
- `--config-dir /path/to/configs` (directory of per-platform YAML configs)

## Extending Platforms

To add a new platform:

1. Add a new YAML file in `agents/<platform>.yaml` with both `agent` and `task` sections.
2. Pass the new platform name via `--platforms` or add it to `DEFAULT_PLATFORMS` in `scripts/pipeline_utils.py`.

## Configuration Files

Each config file lives under `agents/` and contains two sections:

- `agent`: persona settings for the CrewAI agent
- `task`: prompt template plus expected output

Configs included:

- `agents/transcript.yaml`
- `agents/personality.yaml`
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

## Tests

```bash
make test
```

Tests focus on path and output logic so you can change copy rules without breaking IO.
