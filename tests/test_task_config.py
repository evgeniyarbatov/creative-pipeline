import pytest
from task_config import TaskConfigError, load_task_config


def test_load_task_config_defaults(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
  backstory: "Backstory"
task:
  description_template: "Do thing with {transcript}"
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    config = load_task_config(config_file)

    assert config["description_template"]
    assert config["expected_output"] == "Result"


def test_load_task_config_unknown_key(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
  backstory: "Backstory"
task:
  description_template: "Do thing"
  expected_output: "Result"
  extra: "nope"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TaskConfigError):
        load_task_config(config_file)


def test_load_task_config_missing_required(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
  backstory: "Backstory"
task:
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TaskConfigError):
        load_task_config(config_file)


def test_load_task_config_missing_section(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
  backstory: "Backstory"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TaskConfigError):
        load_task_config(config_file)
