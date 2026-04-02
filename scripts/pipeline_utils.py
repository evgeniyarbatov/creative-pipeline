from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from task_config import TaskConfigError

DEFAULT_PLATFORMS = ("facebook", "instagram", "deviantart", "pinterest")


def derive_artwork_name(transcript_path: Path) -> str:
    name = transcript_path.stem.strip()
    if not name:
        raise ValueError(f"Empty artwork name derived from {transcript_path}")
    return name


def build_output_paths(output_dir: Path, platforms: Iterable[str] = DEFAULT_PLATFORMS) -> dict[str, Path]:
    return {platform: output_dir / f"{platform}.txt" for platform in platforms}


def normalize_personality_outputs(output_dir: Path, platforms: Iterable[str]) -> None:
    for platform in platforms:
        output_path = output_dir / f"{platform}.txt"
        raw = output_path.read_text(encoding="utf-8").strip()
        if not raw:
            raise TaskConfigError(f"Empty personality output for {platform}: {output_path}")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            raise TaskConfigError(f"Personality output JSON must be an object: {output_path}")
        post_text = parsed.get("post_text")
        if not isinstance(post_text, str) or not post_text.strip():
            raise TaskConfigError(f"Personality output missing 'post_text': {output_path}")
        output_path.write_text(post_text.strip(), encoding="utf-8")
