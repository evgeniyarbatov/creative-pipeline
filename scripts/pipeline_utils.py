from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from task_config import TaskConfigError

PERSONALITY_DIRNAME = "personality"


def derive_artwork_name(transcript_path: Path) -> str:
    name = transcript_path.stem.strip()
    if not name or (transcript_path.name.startswith(".") and transcript_path.suffix == ""):
        raise ValueError(f"Empty artwork name derived from {transcript_path}")
    return name


def build_output_paths(output_dir: Path, platforms: Iterable[str]) -> dict[str, Path]:
    return {platform: output_dir / f"{platform}.txt" for platform in platforms}


def personality_output_dir(output_dir: Path) -> Path:
    return output_dir / PERSONALITY_DIRNAME


def build_personality_output_paths(
    output_dir: Path,
    platforms: Iterable[str],
) -> dict[str, Path]:
    base_dir = personality_output_dir(output_dir)
    return {platform: base_dir / f"{platform}.txt" for platform in platforms}


HASHTAG_RE = re.compile(r"(?<!\w)#(?=\w*[A-Za-z])\w+")


def strip_hashtags(text: str) -> str:
    cleaned = HASHTAG_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n[ \t]+", "\n", cleaned)
    return cleaned.strip()


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
        tag = re.sub(r"^#+", "", tag)
        tag = tag.strip(" \t.,;:!?\"'()[]{}")
        if not tag:
            continue
        tag = re.split(r"[\s-]+", tag)[0]
        if not tag:
            continue
        if tag not in seen:
            tags.append(tag)
            seen.add(tag)

    if not tags:
        raise TaskConfigError(f"Tags output contained no usable tags: {output_path}")

    output_path.write_text("\n".join(tags), encoding="utf-8")


def normalize_personality_outputs(output_dir: Path, platforms: Iterable[str]) -> None:
    personality_dir = personality_output_dir(output_dir)
    for platform in platforms:
        output_path = personality_dir / f"{platform}.txt"
        raw = output_path.read_text(encoding="utf-8").strip()
        if not raw:
            raise TaskConfigError(f"Empty personality output for {platform}: {output_path}")
        text = raw
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if parsed is not None:
            if not isinstance(parsed, dict):
                raise TaskConfigError(f"Personality output JSON must be an object: {output_path}")
            post_text = parsed.get("post_text")
            if not isinstance(post_text, str) or not post_text.strip():
                raise TaskConfigError(f"Personality output missing 'post_text': {output_path}")
            text = post_text.strip()

        text = strip_hashtags(text)
        if not text:
            raise TaskConfigError(f"Personality output empty after cleanup: {output_path}")
        output_path.write_text(text, encoding="utf-8")
