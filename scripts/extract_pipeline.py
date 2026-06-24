from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

from crewai import Agent, Crew, Process, Task

from agent_config import AgentConfigError, load_agent_config
from task_config import TaskConfigError, load_task_config
from memory_schema import MemorySchemaError, parse_memory_payload, render_memory_markdown
from pipeline_utils import (
    derive_artwork_name,
    normalize_tags_output,
)

MEMORY_FILENAME = "memory.json"
MEMORY_MD_FILENAME = "memory.md"
TAGS_FILENAME = "tags.txt"

EXTRACTION_OPTIONS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_predict": 1024,
}
DERIVATION_OPTIONS = {
    "temperature": 0.4,
    "top_p": 0.85,
    "repeat_penalty": 1.15,
    "num_predict": 120,
}


def memory_path(output_dir: Path) -> Path:
    return output_dir / MEMORY_FILENAME


def memory_md_path(output_dir: Path) -> Path:
    return output_dir / MEMORY_MD_FILENAME


def tags_output_path(output_dir: Path) -> Path:
    return output_dir / TAGS_FILENAME


def extraction_options() -> dict[str, float | int]:
    return dict(EXTRACTION_OPTIONS)


def derivation_options() -> dict[str, float | int]:
    return dict(DERIVATION_OPTIONS)


def output_text_ready(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def base_output_paths(output_dir: Path) -> list[Path]:
    return [
        memory_path(output_dir),
        memory_md_path(output_dir),
        tags_output_path(output_dir),
    ]


def outputs_complete(paths: Iterable[Path]) -> bool:
    return all(output_text_ready(path) for path in paths)


def read_required_text(path: Path, label: str) -> str:
    if not path.exists():
        raise TaskConfigError(f"Missing {label} output: {path}")
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise TaskConfigError(f"Empty {label} output: {path}")
    return raw


def write_output_file(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, dict):
        payload = json.dumps(content, ensure_ascii=False, indent=2)
    else:
        payload = str(content)
    path.write_text(payload, encoding="utf-8")


def persist_task_output(task: Task, output_path: Path, label: str) -> None:
    if task.output is None:
        raise TaskConfigError(f"Missing {label} output: {output_path}")
    write_output_file(output_path, task.output.raw)


def persist_memory_output(
    task: Task, output_dir: Path, artwork_name: str
) -> None:
    if task.output is None:
        raise TaskConfigError(f"Missing memory output: {memory_path(output_dir)}")
    try:
        memory = parse_memory_payload(task.output.raw)
    except MemorySchemaError as exc:
        raise TaskConfigError(
            f"Malformed memory output for {artwork_name}: {exc}"
        ) from exc
    write_output_file(memory_path(output_dir), memory)
    write_output_file(
        memory_md_path(output_dir), render_memory_markdown(memory, artwork_name)
    )


def get_llm(model_name: str, base_url: str | None, options: dict[str, float | int]):
    try:
        from crewai import LLM

        kwargs = {"extra_body": {"options": options}}
        if base_url:
            kwargs["base_url"] = base_url
        return LLM(model=f"ollama/{model_name}", **kwargs)
    except Exception:
        try:
            from langchain_community.llms import Ollama
        except Exception:  # pragma: no cover - fallback when community package missing
            from langchain_ollama import Ollama

        kwargs = {"options": options}
        if base_url:
            kwargs["base_url"] = base_url
        return Ollama(model=model_name, **kwargs)


def build_agents(
    extraction_llm,
    derivation_llm,
    config_dir: Path,
) -> dict[str, Agent]:
    def build_agent(name: str, llm) -> Agent:
        config = load_agent_config(config_dir / f"{name}.yaml")
        return Agent(**config, llm=llm)

    return {
        "transcript": build_agent("transcript", extraction_llm),
        "tags": build_agent("tags", derivation_llm),
    }


def load_task_configs(config_dir: Path) -> dict[str, dict[str, str]]:
    return {
        "transcript": load_task_config(config_dir / "transcript.yaml"),
        "tags": load_task_config(config_dir / "tags.yaml"),
    }


def build_transcript_task(
    agents: dict[str, Agent],
    task_configs: dict[str, dict[str, str]],
    transcript_text: str,
    output_dir: Path,
) -> Task:
    transcript_config = task_configs["transcript"]
    return Task(
        description=(
            transcript_config["description_template"].format(
                transcript=transcript_text,
            )
        ),
        expected_output=transcript_config["expected_output"],
        agent=agents["transcript"],
    )


def build_tags_task(
    agents: dict[str, Agent],
    task_configs: dict[str, dict[str, str]],
    memory_context: str,
    output_dir: Path,
) -> Task:
    tags_config = task_configs["tags"]
    return Task(
        description=(
            tags_config["description_template"].format(
                transcript=memory_context,
            )
        ),
        expected_output=tags_config["expected_output"],
        agent=agents["tags"],
    )



def process_transcript(
    transcript_path: Path,
    output_root: Path,
    extraction_llm,
    derivation_llm,
    config_dir: Path,
    task_configs: dict[str, dict[str, str]],
) -> None:
    transcript_text = transcript_path.read_text(encoding="utf-8").strip()
    if not transcript_text:
        print(f"Skipping empty transcript: {transcript_path}")
        return

    artwork_name = derive_artwork_name(transcript_path)
    output_dir = output_root / artwork_name
    output_dir.mkdir(parents=True, exist_ok=True)

    if outputs_complete(base_output_paths(output_dir)):
        print(f"Skipping {transcript_path} (outputs already present).")
        return

    agents = build_agents(extraction_llm, derivation_llm, config_dir)

    # Step 2: extract a structured memory from the transcript.
    transcript_task = build_transcript_task(agents, task_configs, transcript_text, output_dir)
    transcript_crew = Crew(
        agents=[agents["transcript"]],
        tasks=[transcript_task],
        process=Process.sequential,
        verbose=True,
    )
    transcript_crew.kickoff()
    persist_memory_output(transcript_task, output_dir, artwork_name)

    memory_context = read_required_text(memory_md_path(output_dir), "memory")

    # Step 3: generate tags (legacy, opt-in derivation).
    tag_task = build_tags_task(agents, task_configs, memory_context, output_dir)

    tags_crew = Crew(
        agents=[agents["tags"]],
        tasks=[tag_task],
        process=Process.sequential,
        verbose=True,
    )
    tags_crew.kickoff()
    persist_task_output(
        tag_task,
        tags_output_path(output_dir),
        "tags",
    )
    normalize_tags_output(tags_output_path(output_dir))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract artist memory from art transcripts.")
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
        default="gemma3:latest",
        help="Ollama model name (default: gemma3:latest).",
    )
    parser.add_argument(
        "--ollama-base-url",
        default=os.environ.get("OLLAMA_BASE_URL"),
        help="Optional Ollama base URL (overrides OLLAMA_BASE_URL env var).",
    )
    parser.add_argument(
        "--config-dir",
        default=default_config_dir,
        help="Directory containing the agent + task YAML configs.",
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
    args = parser.parse_args()

    transcripts_dir = Path(args.transcripts_dir).expanduser()
    if not transcripts_dir.exists():
        raise SystemExit(f"Transcript directory not found: {transcripts_dir}")

    output_root = Path(args.output_dir).expanduser() if args.output_dir else transcripts_dir

    extraction_llm = get_llm(args.model, args.ollama_base_url, extraction_options())
    derivation_llm = get_llm(args.model, args.ollama_base_url, derivation_options())
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
        task_configs = load_task_configs(configs_dir)
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
                extraction_llm,
                derivation_llm,
                configs_dir,
                task_configs,
            )
        except (AgentConfigError, TaskConfigError) as exc:
            raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
