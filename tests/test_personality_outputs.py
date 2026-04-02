import pytest

from pipeline_utils import normalize_personality_outputs
from task_config import TaskConfigError


def test_normalize_personality_outputs_json(tmp_path):
    output_path = tmp_path / "instagram.txt"
    output_path.write_text('{"post_text":"Hello world"}', encoding="utf-8")

    normalize_personality_outputs(tmp_path, ["instagram"])

    assert output_path.read_text(encoding="utf-8") == "Hello world"


def test_normalize_personality_outputs_plain_text(tmp_path):
    output_path = tmp_path / "instagram.txt"
    output_path.write_text("Hello world", encoding="utf-8")

    normalize_personality_outputs(tmp_path, ["instagram"])

    assert output_path.read_text(encoding="utf-8") == "Hello world"


def test_normalize_personality_outputs_missing_post_text(tmp_path):
    output_path = tmp_path / "instagram.txt"
    output_path.write_text('{"text":"Hello world"}', encoding="utf-8")

    with pytest.raises(TaskConfigError):
        normalize_personality_outputs(tmp_path, ["instagram"])
