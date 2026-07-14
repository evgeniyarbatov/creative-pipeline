from pathlib import Path

from task_config import load_task_config


def test_tag_prompt_requires_single_words() -> None:
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    config = load_task_config(agents_dir / "tags.yaml")
    description = config["description_template"].lower()
    assert "single words" in description
