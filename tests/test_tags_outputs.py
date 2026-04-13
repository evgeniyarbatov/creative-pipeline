import pytest

from pipeline_utils import normalize_tags_output
from task_config import TaskConfigError


def test_normalize_tags_output_single_words(tmp_path):
    output_path = tmp_path / "tags.txt"
    output_path.write_text("- Blue sky\n* #Oil-Painting\n1. ABSTRACT art\n", encoding="utf-8")

    normalize_tags_output(output_path)

    assert output_path.read_text(encoding="utf-8") == "\n".join(
        [
            "- blue",
            "- oil",
            "- abstract",
        ]
    )


def test_normalize_tags_output_empty(tmp_path):
    output_path = tmp_path / "tags.txt"
    output_path.write_text("", encoding="utf-8")

    with pytest.raises(TaskConfigError):
        normalize_tags_output(output_path)


def test_normalize_tags_output_dedupes_case_insensitive(tmp_path):
    output_path = tmp_path / "tags.txt"
    output_path.write_text("Sculpture\nsculpture\nSCULPTURE\n", encoding="utf-8")

    normalize_tags_output(output_path)

    assert output_path.read_text(encoding="utf-8") == "- sculpture"
