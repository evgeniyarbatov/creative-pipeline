import pytest

from agent_config import AgentConfigError, load_agent_config


def test_load_agent_config_defaults(tmp_path):
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

    config = load_agent_config(config_file)

    assert config["allow_delegation"] is False
    assert config["verbose"] is False
    assert config["backstory"] == "Backstory"


def test_load_agent_config_missing_backstory_defaults(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
task:
  description_template: "Do thing with {transcript}"
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    config = load_agent_config(config_file)

    assert config["backstory"] == ""


def test_load_agent_config_unknown_key(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  goal: "Capture transcript"
  backstory: "Backstory"
  extra: "nope"
task:
  description_template: "Do thing"
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentConfigError):
        load_agent_config(config_file)


def test_load_agent_config_missing_required(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
agent:
  role: "Transcript"
  backstory: "Backstory"
task:
  description_template: "Do thing"
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentConfigError):
        load_agent_config(config_file)


def test_load_agent_config_missing_section(tmp_path):
    config_file = tmp_path / "transcript.yaml"
    config_file.write_text(
        """
task:
  description_template: "Do thing"
  expected_output: "Result"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentConfigError):
        load_agent_config(config_file)
