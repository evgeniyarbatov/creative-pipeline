from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from task_config import TaskConfigError


def derive_artwork_name(transcript_path: Path) -> str:
    name = transcript_path.stem.strip()
    if not name or (transcript_path.name.startswith(".") and transcript_path.suffix == ""):
        raise ValueError(f"Empty artwork name derived from {transcript_path}")
    return name


def build_output_paths(output_dir: Path, platforms: Iterable[str]) -> dict[str, Path]:
    return {platform: output_dir / f"{platform}.txt" for platform in platforms}


BULLET_PREFIX_RE = re.compile(r"^(?:[-*•]+|\d+[.)])\s*")


def normalize_tags_output(output_path: Path) -> None:
    raw = output_path.read_text(encoding="utf-8").strip()
    if not raw:
        raise TaskConfigError(f"Empty tags output: {output_path}")

    tags: list[str] = []
    seen = set()
    for line in raw.splitlines():
        tag = line.strip()
        if not tag:
            continue
        tag = BULLET_PREFIX_RE.sub("", tag)
        tag = re.sub(r"^#+", "", tag)
        tag = tag.strip(" \t.,;:!?\"'()[]{}")
        if not tag:
            continue
        tag = re.split(r"[\s-]+", tag)[0]
        if not tag:
            continue
        tag = tag.lower()
        if tag not in seen:
            tags.append(tag)
            seen.add(tag)

    if not tags:
        raise TaskConfigError(f"Tags output contained no usable tags: {output_path}")

    output_path.write_text("\n".join(f"- {tag}" for tag in tags), encoding="utf-8")
