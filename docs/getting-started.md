# Getting Started

This pipeline generates social captions from transcript `.txt` files using CrewAI + Ollama.

## Requirements

- Python 3.12
- Ollama running locally

## Install

```bash
ollama pull gemma3:latest
make install
```

## Add Transcripts

Default input directory:

- `~/Documents/art-talks`

Each transcript should be a plain text file:

- `~/Documents/art-talks/<artwork-name>.txt`

`<artwork-name>` becomes the output folder name.

## Run

```bash
make run-captions
```

By default, outputs are written under `~/Documents/art-talks/<artwork-name>/`.

## Outputs

Per transcript, the pipeline creates:

- `~/Documents/art-talks/<artwork-name>/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/personality/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/personality/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/personality/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/personality/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/tags.txt`
- `~/Documents/art-talks/<artwork-name>/transcript_analysis.json`

## Data Notes

Transcripts and generated captions live outside the repo. This repo does not include personal transcript data.
