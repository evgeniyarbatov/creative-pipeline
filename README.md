# Creative Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?logo=llama&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent%20AI-purple)

Extracts artist memory from raw transcripts using CrewAI + Ollama — not captions, not marketing copy. The goal is to preserve what you were thinking when you made a piece, including the parts that never resolved. See `ROADMAP.md` and `docs/philosophy.md` for the full direction.

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
- Principles behind the output format: `docs/philosophy.md`

## License

MIT. See `LICENSE.md`.
