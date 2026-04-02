from pathlib import Path

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
