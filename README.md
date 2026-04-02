# Creative Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=llama&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent%20AI-purple)

Generate platform-specific social captions from transcript files using CrewAI + Ollama.

## Examples

See sample output in `examples/`.

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
make
```

## Docs

- Getting started and transcripts: `docs/getting-started.md`
- Voice Memos transcript steps: `docs/transcripts.md`
- Configuration and CLI options: `docs/configuration.md`

## License

MIT. See `LICENSE.md`.
