# Creative Pipeline: Social Caption Generator

Generate platform-specific social captions from transcript files using CrewAI + Ollama.

## Quick Start

1. Install and run Ollama.
2. Pull the default model:

```bash
ollama pull gemma3:latest
```

3. Install dependencies:

```bash
make install
```

4. Add a transcript `.txt` file.
5. Run the pipeline:

```bash
make run-captions
```

## Requirements

- Python 3.12
- Ollama running locally

## Docs

- Getting started and transcripts: `docs/getting-started.md`
- Voice Memos transcript steps: `docs/transcripts.md`
- Configuration and CLI options: `docs/configuration.md`

## License

MIT. See `LICENSE.md`.
