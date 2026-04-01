from pathlib import Path

import pytest

from pipeline_utils import build_output_paths, derive_artwork_name, find_optional_context


def test_derive_artwork_name():
    path = Path("/tmp/Sunrise Study.txt")
    assert derive_artwork_name(path) == "Sunrise Study"


def test_derive_artwork_name_empty():
    path = Path("/tmp/.txt")
    with pytest.raises(ValueError):
        derive_artwork_name(path)


def test_build_output_paths():
    output_dir = Path("/tmp/output")
    paths = build_output_paths(output_dir, ["facebook", "instagram"])
    assert paths["facebook"] == output_dir / "facebook.txt"
    assert paths["instagram"] == output_dir / "instagram.txt"


def test_find_optional_context_sidecar(tmp_path):
    transcript = tmp_path / "art.txt"
    transcript.write_text("Transcript text", encoding="utf-8")
    sidecar = tmp_path / "art.context.md"
    sidecar.write_text("Extra context", encoding="utf-8")

    assert find_optional_context(transcript) == "Extra context"


def test_find_optional_context_context_dir(tmp_path):
    transcript = tmp_path / "art.txt"
    transcript.write_text("Transcript text", encoding="utf-8")
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    context_file = context_dir / "art.txt"
    context_file.write_text("Context folder text", encoding="utf-8")

    assert find_optional_context(transcript) == "Context folder text"


def test_find_optional_context_json(tmp_path):
    transcript = tmp_path / "art.txt"
    transcript.write_text("Transcript text", encoding="utf-8")
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    context_file = context_dir / "art.json"
    context_file.write_text("{\"medium\": \"ink\"}", encoding="utf-8")

    assert find_optional_context(transcript) == '{\n  "medium": "ink"\n}'
