from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable

from crewai import Agent, Crew, Process, Task

from agent_config import AgentConfigError, load_agent_config
from task_config import TaskConfigError, load_task_config
from pipeline_utils import DEFAULT_PLATFORMS, build_output_paths, derive_artwork_name, find_optional_context


def get_llm(model_name: str, base_url: str | None):
    try:
        from crewai import LLM

        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        return LLM(model=f"ollama/{model_name}", **kwargs)
    except Exception:
        try:
            from langchain_community.llms import Ollama
        except Exception:  # pragma: no cover - fallback when community package missing
            from langchain_ollama import Ollama

        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        return Ollama(model=model_name, **kwargs)


def build_agents(llm, config_dir: Path, platforms: Iterable[str]) -> dict[str, Agent]:
    def build_agent(name: str) -> Agent:
        config = load_agent_config(config_dir / f"{name}.yaml")
        return Agent(**config, llm=llm)

    agents: dict[str, Agent] = {
        "voice": build_agent("voice"),
        "personality": build_agent("personality"),
        "tags": build_agent("tags"),
    }

    for platform in platforms:
        agents[platform] = build_agent(platform)

    return agents


def load_task_configs(config_dir: Path, platforms: Iterable[str]) -> dict[str, dict[str, str]]:
    task_configs = {
        "voice": load_task_config(config_dir / "voice.yaml"),
        "personality": load_task_config(config_dir / "personality.yaml"),
        "tags": load_task_config(config_dir / "tags.yaml"),
    }

    for platform in platforms:
        task_configs[platform] = load_task_config(config_dir / f"{platform}.yaml")

    return task_configs


def build_tasks(
    agents: dict[str, Agent],
    task_configs: dict[str, dict[str, str]],
    transcript_text: str,
    context_text: str | None,
    output_dir: Path,
    platforms: Iterable[str],
) -> list[Task]:
    context_value = context_text or "None provided."
    voice_config = task_configs["voice"]
    voice_task = Task(
        description=(
            voice_config["description_template"].format(
                transcript=transcript_text,
                context=context_value,
            )
        ),
        expected_output=voice_config["expected_output"],
        agent=agents["voice"],
    )

    tags_path = output_dir / "tags.txt"
    tags_config = task_configs["tags"]
    tag_task = Task(
        description=(
            tags_config["description_template"].format(
                transcript=transcript_text,
                context=context_value,
            )
        ),
        expected_output=tags_config["expected_output"],
        agent=agents["tags"],
        output_file=str(tags_path),
    )

    tasks = [voice_task, tag_task]

    for platform in platforms:
        config = task_configs[platform]
        display_name = config.get("display_name", platform.title())
        style_rules = config.get("style_rules", "")
        output_rules = config.get("output_rules", "")
        output_path = output_dir / f"{platform}.txt"
        description = config["description_template"].format(
            display_name=display_name,
            style_rules=style_rules,
            output_rules=output_rules,
            transcript=transcript_text,
            context=context_value,
        )

        tasks.append(
            Task(
                description=description,
                expected_output=config["expected_output"].format(display_name=display_name),
                agent=agents[platform],
                context=[voice_task, tag_task],
                output_file=str(output_path),
            )
        )

    return tasks


def build_personality_tasks(
    agents: dict[str, Agent],
    task_configs: dict[str, dict[str, str]],
    output_dir: Path,
    platforms: Iterable[str],
) -> list[Task]:
    personality_config = task_configs["personality"]
    tasks: list[Task] = []

    for platform in platforms:
        output_path = output_dir / f"{platform}.txt"
        if not output_path.exists():
            raise TaskConfigError(f"Missing platform output for personality styling: {output_path}")
        post_text = output_path.read_text(encoding="utf-8").strip()
        if not post_text:
            raise TaskConfigError(f"Empty platform output for personality styling: {output_path}")

        display_name = task_configs.get(platform, {}).get("display_name", platform.title())
        description = personality_config["description_template"].format(
            post_text=post_text,
            display_name=display_name,
            platform=platform,
        )
        expected_output = personality_config["expected_output"].format(display_name=display_name)

        tasks.append(
            Task(
                description=description,
                expected_output=expected_output,
                agent=agents["personality"],
                output_file=str(output_path),
            )
        )

    return tasks


def process_transcript(
    transcript_path: Path,
    output_root: Path,
    platforms: Iterable[str],
    llm,
    config_dir: Path,
    task_configs: dict[str, dict[str, str]],
    dry_run: bool,
) -> None:
    transcript_text = transcript_path.read_text(encoding="utf-8").strip()
    if not transcript_text:
        print(f"Skipping empty transcript: {transcript_path}")
        return

    artwork_name = derive_artwork_name(transcript_path)
    output_dir = output_root / artwork_name
    output_dir.mkdir(parents=True, exist_ok=True)

    context_text = find_optional_context(transcript_path)
    if context_text:
        print(f"Loaded context for {artwork_name}")

    if dry_run:
        output_paths = build_output_paths(output_dir, platforms)
        print(f"[Dry run] Would write outputs to {output_dir}")
        for platform, path in output_paths.items():
            print(f"  - {platform}: {path}")
        print(f"  - tags: {output_dir / 'tags.txt'}")
        print("  - personality: would rewrite each platform caption after generation")
        return

    agents = build_agents(llm, config_dir, platforms)
    tasks = build_tasks(agents, task_configs, transcript_text, context_text, output_dir, platforms)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    personality_tasks = build_personality_tasks(agents, task_configs, output_dir, platforms)
    personality_crew = Crew(
        agents=[agents["personality"]],
        tasks=personality_tasks,
        process=Process.sequential,
        verbose=True,
    )
    personality_crew.kickoff()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate social captions from art transcripts.")
    default_config_dir = str(Path(__file__).resolve().parents[1] / "agents")
    parser.add_argument(
        "--transcripts-dir",
        default=os.path.expanduser("~/Documents/art-talks"),
        help="Directory containing transcript .txt files.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Optional output root (defaults to transcripts dir)."
            " Each artwork will have its own subfolder."
        ),
    )
    parser.add_argument(
        "--model",
        default="phi3:mini",
        help="Ollama model name (default: phi3:mini).",
    )
    parser.add_argument(
        "--ollama-base-url",
        default=os.environ.get("OLLAMA_BASE_URL"),
        help="Optional Ollama base URL (overrides OLLAMA_BASE_URL env var).",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=list(DEFAULT_PLATFORMS),
        help="Platforms to generate (default: all).",
    )
    parser.add_argument(
        "--config-dir",
        default=default_config_dir,
        help="Directory containing per-platform YAML configs (agent + task sections).",
    )
    parser.add_argument(
        "--agents-dir",
        default=None,
        help="Deprecated alias for --config-dir.",
    )
    parser.add_argument(
        "--tasks-dir",
        default=None,
        help="Deprecated alias for --config-dir.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned outputs without calling the model.",
    )

    args = parser.parse_args()

    transcripts_dir = Path(args.transcripts_dir).expanduser()
    if not transcripts_dir.exists():
        raise SystemExit(f"Transcript directory not found: {transcripts_dir}")

    output_root = Path(args.output_dir).expanduser() if args.output_dir else transcripts_dir

    platforms = [platform.lower() for platform in args.platforms]

    llm = get_llm(args.model, args.ollama_base_url)
    override_dirs = [value for value in (args.agents_dir, args.tasks_dir) if value]
    if override_dirs:
        if len(set(override_dirs)) > 1:
            raise SystemExit("--agents-dir and --tasks-dir must match; configs are unified.")
        if args.config_dir != default_config_dir and args.config_dir != override_dirs[0]:
            raise SystemExit("--config-dir cannot be combined with --agents-dir/--tasks-dir.")
        config_dir = override_dirs[0]
    else:
        config_dir = args.config_dir

    configs_dir = Path(config_dir).expanduser()
    if not configs_dir.exists():
        raise SystemExit(f"Config directory not found: {configs_dir}")
    try:
        task_configs = load_task_configs(configs_dir, platforms)
    except TaskConfigError as exc:
        raise SystemExit(str(exc)) from exc

    transcript_files = sorted(transcripts_dir.glob("*.txt"))
    if not transcript_files:
        print(f"No .txt transcripts found in {transcripts_dir}")
        return

    for transcript_path in transcript_files:
        try:
            process_transcript(
                transcript_path,
                output_root,
                platforms,
                llm,
                configs_dir,
                task_configs,
                args.dry_run,
            )
        except (AgentConfigError, TaskConfigError) as exc:
            raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
