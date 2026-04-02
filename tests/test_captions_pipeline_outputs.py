from types import SimpleNamespace

import pytest

from captions_pipeline import output_dir_complete, output_text_ready, persist_task_output, write_output_file
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


def test_output_dir_complete_true_when_all_outputs_present(tmp_path):
    output_dir = tmp_path / "artwork"
    output_dir.mkdir()
    (output_dir / "transcript_analysis.txt").write_text("analysis", encoding="utf-8")
    (output_dir / "tags.txt").write_text("tag1\ntag2", encoding="utf-8")
    (output_dir / "instagram.txt").write_text("caption", encoding="utf-8")

    assert output_dir_complete(output_dir, ["instagram"]) is True


def test_output_dir_complete_false_when_any_output_missing(tmp_path):
    output_dir = tmp_path / "artwork"
    output_dir.mkdir()
    (output_dir / "transcript_analysis.txt").write_text("analysis", encoding="utf-8")
    (output_dir / "tags.txt").write_text("tag1\ntag2", encoding="utf-8")

    assert output_dir_complete(output_dir, ["instagram"]) is False
