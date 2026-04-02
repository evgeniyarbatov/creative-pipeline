from types import SimpleNamespace

import pytest

from captions_pipeline import persist_task_output, write_output_file
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
