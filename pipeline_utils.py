from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

DEFAULT_PLATFORMS = ("facebook", "instagram", "deviantart", "pinterest")


def derive_artwork_name(transcript_path: Path) -> str:
    name = transcript_path.stem.strip()
    if not name:
        raise ValueError(f"Empty artwork name derived from {transcript_path}")
    return name


def build_output_paths(output_dir: Path, platforms: Iterable[str] = DEFAULT_PLATFORMS) -> dict[str, Path]:
    return {platform: output_dir / f"{platform}.txt" for platform in platforms}


def find_optional_context(transcript_path: Path) -> str | None:
    stem = transcript_path.stem
    parent = transcript_path.parent

    candidates = [
        transcript_path.with_suffix(".context.txt"),
        transcript_path.with_suffix(".context.md"),
        parent / "context" / f"{stem}.txt",
        parent / "context" / f"{stem}.md",
        parent / "context" / f"{stem}.json",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            if candidate.suffix == ".json":
                raw = json.loads(candidate.read_text(encoding="utf-8"))
                return json.dumps(raw, indent=2, ensure_ascii=True)
            return candidate.read_text(encoding="utf-8").strip()

    return None
