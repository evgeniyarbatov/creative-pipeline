import pytest
from pipeline_utils import normalize_caption_output
from task_config import TaskConfigError


def test_normalize_caption_output_keeps_first_sentence(tmp_path):
    output_path = tmp_path / "caption.txt"
    output_path.write_text("First sentence. Second sentence follows.", encoding="utf-8")

    normalize_caption_output(output_path)

    assert output_path.read_text(encoding="utf-8") == "First sentence."


def test_normalize_caption_output_collapses_lines(tmp_path):
    output_path = tmp_path / "caption.txt"
    output_path.write_text("One line\nTwo line", encoding="utf-8")

    normalize_caption_output(output_path)

    assert output_path.read_text(encoding="utf-8") == "One line Two line"


def test_normalize_caption_output_empty(tmp_path):
    output_path = tmp_path / "caption.txt"
    output_path.write_text("", encoding="utf-8")

    with pytest.raises(TaskConfigError):
        normalize_caption_output(output_path)
