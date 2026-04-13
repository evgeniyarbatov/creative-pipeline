# Getting Started

This pipeline generates bullet-point caption ideas from transcript `.txt` files using CrewAI + Ollama.

## Add Transcripts

Default input directory:

- `~/Documents/art-talks`

Each transcript should be a plain text file:

- `~/Documents/art-talks/<artwork-name>.txt`

`<artwork-name>` becomes the output folder name.

## Run

```bash
make
```

By default, outputs are written under `~/Documents/art-talks/<artwork-name>/`.

## Outputs

Per transcript, the pipeline creates bullet-point idea lists:

- `~/Documents/art-talks/<artwork-name>/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/personality/facebook.txt`
- `~/Documents/art-talks/<artwork-name>/personality/instagram.txt`
- `~/Documents/art-talks/<artwork-name>/personality/deviantart.txt`
- `~/Documents/art-talks/<artwork-name>/personality/pinterest.txt`
- `~/Documents/art-talks/<artwork-name>/tags.txt`
- `~/Documents/art-talks/<artwork-name>/transcript_analysis.json` (bullet points, despite the extension)

## Data Notes

Transcripts and generated bullet-point outputs live outside the repo.
