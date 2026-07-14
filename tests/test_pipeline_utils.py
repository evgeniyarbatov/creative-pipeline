from pathlib import Path

import pytest
from pipeline_utils import derive_artwork_name


def test_derive_artwork_name() -> None:
    path = Path("/transcripts/Sunrise Study.txt")
    assert derive_artwork_name(path) == "Sunrise Study"


def test_derive_artwork_name_empty() -> None:
    path = Path("/transcripts/.txt")
    with pytest.raises(ValueError):
        derive_artwork_name(path)
