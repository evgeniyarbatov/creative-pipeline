from pathlib import Path

import pytest

from pipeline_utils import build_output_paths, derive_artwork_name


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
