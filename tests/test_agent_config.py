import pytest

from agent_config import AgentConfigError, load_agent_config


def test_load_agent_config_defaults(tmp_path):
    config_file = tmp_path / "voice.yaml"
    config_file.write_text(
        """
role: "Voice"
goal: "Capture voice"
backstory: "Backstory"
""".strip(),
        encoding="utf-8",
    )

    config = load_agent_config(config_file)

    assert config["allow_delegation"] is False
    assert config["verbose"] is False


def test_load_agent_config_unknown_key(tmp_path):
    config_file = tmp_path / "voice.yaml"
    config_file.write_text(
        """
role: "Voice"
goal: "Capture voice"
backstory: "Backstory"
extra: "nope"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentConfigError):
        load_agent_config(config_file)


def test_load_agent_config_missing_required(tmp_path):
    config_file = tmp_path / "voice.yaml"
    config_file.write_text(
        """
role: "Voice"
backstory: "Backstory"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(AgentConfigError):
        load_agent_config(config_file)
