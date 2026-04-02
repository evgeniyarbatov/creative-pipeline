from types import SimpleNamespace

import pytest

from captions_pipeline import (
    base_output_paths,
    output_text_ready,
    outputs_complete,
    persist_task_output,
    personality_output_paths,
    write_output_file,
)
from pipeline_utils import personality_output_dir
from task_config import TaskConfigError


def test_write_output_file_string(tmp_path):
    output_path = tmp_path / "output.txt"

    write_output_file(output_path, "hello")

    assert output_path.read_text(encoding="utf-8") == "hello"


def test_write_output_file_dict(tmp_path):
    output_path = tmp_path / "output.json"

    write_output_file(output_path, {"a": 1})

    assert output_path.read_text(encoding="utf-8") == '{\n  "a": 1\n}'


def test_persist_task_output_missing_output(tmp_path):
    output_path = tmp_path / "output.txt"
    task = SimpleNamespace(output=None)

    with pytest.raises(TaskConfigError):
        persist_task_output(task, output_path, "missing")


def test_persist_task_output_writes_raw(tmp_path):
    output_path = tmp_path / "output.txt"
    task = SimpleNamespace(output=SimpleNamespace(raw="payload"))

    persist_task_output(task, output_path, "payload")

    assert output_path.read_text(encoding="utf-8") == "payload"


def test_output_text_ready_false_for_missing_file(tmp_path):
    output_path = tmp_path / "missing.txt"

    assert output_text_ready(output_path) is False


def test_outputs_complete_true_when_all_base_outputs_present(tmp_path):
    output_dir = tmp_path / "artwork"
    output_dir.mkdir()
    (output_dir / "transcript_analysis.txt").write_text("analysis", encoding="utf-8")
    (output_dir / "tags.txt").write_text("tag1\ntag2", encoding="utf-8")
    (output_dir / "instagram.txt").write_text("caption", encoding="utf-8")

    assert outputs_complete(base_output_paths(output_dir, ["instagram"])) is True


def test_outputs_complete_false_when_any_base_output_missing(tmp_path):
    output_dir = tmp_path / "artwork"
    output_dir.mkdir()
    (output_dir / "transcript_analysis.txt").write_text("analysis", encoding="utf-8")
    (output_dir / "tags.txt").write_text("tag1\ntag2", encoding="utf-8")

    assert outputs_complete(base_output_paths(output_dir, ["instagram"])) is False


def test_outputs_complete_personality_outputs(tmp_path):
    output_dir = tmp_path / "artwork"
    output_dir.mkdir()
    personality_dir = personality_output_dir(output_dir)
    personality_dir.mkdir(parents=True, exist_ok=True)
    (personality_dir / "instagram.txt").write_text("styled caption", encoding="utf-8")

    assert outputs_complete(personality_output_paths(output_dir, ["instagram"])) is True
