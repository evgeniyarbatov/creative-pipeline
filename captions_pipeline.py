from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from crewai import Agent, Crew, Process, Task

from agent_config import AgentConfigError, load_agent_config
from pipeline_utils import DEFAULT_PLATFORMS, build_output_paths, derive_artwork_name, find_optional_context


@dataclass(frozen=True)
class PlatformRule:
    display_name: str
    style_rules: str
    output_rules: str


PLATFORM_RULES: dict[str, PlatformRule] = {
    "facebook": PlatformRule(
        display_name="Facebook",
        style_rules=(
            "Friendly and conversational. 1 to 2 short paragraphs."
            " Light storytelling about the piece and process."
            " End with a gentle question or invitation to comment."
        ),
        output_rules="No more than 800 characters. Avoid more than 2 hashtags.",
    ),
    "instagram": PlatformRule(
        display_name="Instagram",
        style_rules=(
            "Vivid, visual, and compact. Use line breaks for rhythm."
            " Focus on mood, materials, and a single memorable detail."
        ),
        output_rules=(
            "Aim for 400 to 900 characters."
            " Include 3 to 8 hashtags derived from the tag list if relevant."
        ),
    ),
    "deviantart": PlatformRule(
        display_name="DeviantArt",
        style_rules=(
            "Art-community tone. Mention medium, tools, or process."
            " Share a short insight about intent or experimentation."
        ),
        output_rules="Aim for 500 to 1200 characters. Avoid hashtags unless truly natural.",
    ),
    "pinterest": PlatformRule(
        display_name="Pinterest",
        style_rules=(
            "Search-friendly and concise. Emphasize subject, style, and use-case."
            " Keep it skimmable with a clear lead sentence."
        ),
        output_rules="Keep it under 500 characters. Include 2 to 4 keywords or hashtags.",
    ),
}


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


def build_agents(llm, agents_dir: Path) -> dict[str, Agent]:
    def build_agent(name: str) -> Agent:
        config = load_agent_config(agents_dir / f"{name}.yaml")
        return Agent(**config, llm=llm)

    agents: dict[str, Agent] = {
        "voice": build_agent("voice"),
        "tags": build_agent("tags"),
    }

    for platform in PLATFORM_RULES:
        agents[platform] = build_agent(platform)

    return agents


def build_tasks(
    agents: dict[str, Agent],
    transcript_text: str,
    context_text: str | None,
    output_dir: Path,
    platforms: Iterable[str],
) -> list[Task]:
    voice_task = Task(
        description=(
            "Analyze the transcript and produce a concise voice guide."
            " Include tone, sentence rhythm, favorite phrases, and do/don't rules."
            " Also summarize the artwork in 2 sentences using the artist's language.\n\n"
            f"Transcript:\n{transcript_text}\n\n"
            f"Additional context:\n{context_text or 'None provided.'}"
        ),
        expected_output=(
            "Voice guide with 5 to 8 bullet points, plus a 2-sentence artwork summary."
        ),
        agent=agents["voice"],
    )

    tags_path = output_dir / "tags.txt"
    tag_task = Task(
        description=(
            "Generate a tag list for the artwork."
            " Focus on subject, medium, style, mood, and themes."
            " Use short phrases (1 to 3 words). No hashtags. One tag per line.\n\n"
            f"Transcript:\n{transcript_text}\n\n"
            f"Additional context:\n{context_text or 'None provided.'}"
        ),
        expected_output="8 to 20 tags, one per line.",
        agent=agents["tags"],
        output_file=str(tags_path),
    )

    tasks = [voice_task, tag_task]

    for platform in platforms:
        rule = PLATFORM_RULES[platform]
        output_path = output_dir / f"{platform}.txt"
        description = (
            f"Write a {rule.display_name} caption for the artwork in the artist's voice."
            f" Style rules: {rule.style_rules}"
            f" Output rules: {rule.output_rules}\n\n"
            "Use the voice guide and summary below."
            " Do not include section headers or analysis."
            " Return only the caption text.\n\n"
            f"Transcript:\n{transcript_text}\n\n"
            f"Additional context:\n{context_text or 'None provided.'}"
        )

        tasks.append(
            Task(
                description=description,
                expected_output=f"A {rule.display_name} caption only.",
                agent=agents[platform],
                context=[voice_task, tag_task],
                output_file=str(output_path),
            )
        )

    return tasks


def process_transcript(
    transcript_path: Path,
    output_root: Path,
    platforms: Iterable[str],
    llm,
    agents_dir: Path,
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
        return

    agents = build_agents(llm, agents_dir)
    tasks = build_tasks(agents, transcript_text, context_text, output_dir, platforms)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate social captions from art transcripts.")
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
        "--agents-dir",
        default=str(Path(__file__).resolve().parent / "config" / "agents"),
        help="Directory containing per-agent YAML configs.",
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
    unknown = [p for p in platforms if p not in PLATFORM_RULES]
    if unknown:
        raise SystemExit(f"Unknown platforms: {', '.join(unknown)}")

    llm = get_llm(args.model, args.ollama_base_url)
    agents_dir = Path(args.agents_dir).expanduser()
    if not agents_dir.exists():
        raise SystemExit(f"Agent config directory not found: {agents_dir}")

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
                agents_dir,
                args.dry_run,
            )
        except AgentConfigError as exc:
            raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
