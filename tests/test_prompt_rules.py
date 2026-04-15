from pathlib import Path

from agent_config import load_agent_config
from task_config import load_task_config


def test_platform_prompts_forbid_hashtags():
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    for platform in ("facebook", "instagram", "deviantart", "pinterest"):
        config = load_task_config(agents_dir / f"{platform}.yaml")
        combined = "\n".join(
            [
                config.get("style_rules", ""),
                config.get("output_rules", ""),
                config.get("description_template", ""),
            ]
        ).lower()
        assert "do not use hashtags" in combined


def test_tag_prompt_requires_single_words():
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    config = load_task_config(agents_dir / "tags.yaml")
    description = config["description_template"].lower()
    assert "single words" in description


def test_platform_prompts_require_two_to_three_sentences():
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    for platform in ("facebook", "instagram", "deviantart", "pinterest"):
        agent_config = load_agent_config(agents_dir / f"{platform}.yaml")
        task_config = load_task_config(agents_dir / f"{platform}.yaml")
        assert "2-3 sentence" in agent_config["goal"].lower()
        assert "2-3 sentence" in task_config["description_template"].lower()
        assert "2-3" in task_config["expected_output"].lower()
