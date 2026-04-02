from pathlib import Path

from agent_config import load_agent_config
from task_config import load_task_config


def test_agent_configs_load():
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    for config_path in agents_dir.glob("*.yaml"):
        load_agent_config(config_path)
        load_task_config(config_path)
