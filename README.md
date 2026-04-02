# Creative Pipeline: Social Caption Generator

Generate platform-specific social captions from transcript files using CrewAI + Ollama.

## Requirements

- Python 3.12
- Ollama running locally

## Quick Start

1. Install and run Ollama.
2. Pull the default model:

```bash
ollama pull gemma3:latest
```

3. Create the virtual environment and install dependencies:

```bash
make install
```

4. Add at least one transcript `.txt` file (see "Transcripts" below).
5. Run the pipeline:

```bash
make run-captions
```

By default, the pipeline reads transcripts from `~/Documents/art-talks` and writes outputs into a subfolder per artwork.

## What It Produces

For each transcript in `~/Documents/art-talks/*.txt`, the pipeline creates:

- `~/Documents/art-talks/<artwork-name>/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/personality/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/personality/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/personality/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/personality/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/tags.txt` (shared tags for all platforms)
- `~/Documents/art-talks/<artwork-name>/transcript_analysis.txt` (structured extraction used downstream)

`<artwork-name>` is the transcript filename without the `.txt` extension.

## Transcripts

### Where to put them

Default input directory:

- `~/Documents/art-talks`

Each transcript should be a plain text file:

- `~/Documents/art-talks/<artwork-name>.txt`

You can change the input directory with `--transcripts-dir`.

### Getting transcripts from Voice Memos on macOS

1. Open the Voice Memos app.
2. Select a recording.
3. Open the transcript view (the Transcript or speech-bubble icon).
4. Select all text and copy it.
5. Paste into a new file in `~/Documents/art-talks/` named `<artwork-name>.txt`.

Tip: keep filenames short and descriptive. The filename becomes the output folder name.

## Data Notes

Transcripts and generated captions live outside the repo (under `~/Documents/art-talks` by default). This repo does not include personal transcript data.

## High-Level Design

The pipeline is intentionally split into configuration and execution:

- Unified configs live in `agents/*.yaml` with both `agent` and `task` sections.
- Each file defines the agent persona plus the prompt template and expected output.
- The runtime in `scripts/captions_pipeline.py` wires agents + tasks together using CrewAI.

Execution flow per transcript:

1. Load the transcript text.
2. Analyze the transcript (`agents/transcript.yaml`).
3. Generate shared tags (`agents/tags.yaml`).
4. Generate a base caption for each platform.
5. Apply personality styling to each platform caption.

## Usage

```bash
make run-captions
```

Optional flags:

- `--platforms facebook instagram` (generate a subset)
- `--transcripts-dir /path/to/transcripts`
- `--output-dir /path/to/output` (defaults to the transcript dir)
- `--ollama-base-url http://localhost:11434`
- `--config-dir /path/to/configs` (directory of per-platform YAML configs)

## Extending Platforms

To add a new platform:

1. Add a new YAML file in `agents/<platform>.yaml` with both `agent` and `task` sections.
2. Pass the new platform name via `--platforms`, or omit `--platforms` to auto-detect all platform configs in `agents/`.

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

## License

MIT. See `LICENSE`.
