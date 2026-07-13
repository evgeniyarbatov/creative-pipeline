from __future__ import annotations

import json
import re
from typing import Any

REQUIRED_KEYS = (
    "source",
    "threads",
    "contradictions",
    "tangents",
    "open_questions",
    "anchors",
)

LIST_KEYS = ("threads", "contradictions", "tangents", "open_questions", "anchors")

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class MemorySchemaError(ValueError):
    pass


def extract_json_payload(raw: str) -> str:
    text = FENCE_RE.sub("", raw.strip()).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def validate_memory_schema(data: Any) -> None:
    if not isinstance(data, dict):
        raise MemorySchemaError("Memory payload must be a JSON object")

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise MemorySchemaError(f"Memory payload missing keys: {', '.join(missing)}")

    if not isinstance(data["source"], dict):
        raise MemorySchemaError("'source' must be an object")

    for key in LIST_KEYS:
        if not isinstance(data[key], list):
            raise MemorySchemaError(f"'{key}' must be a list")

    for key in ("threads", "contradictions", "tangents", "anchors"):
        for index, item in enumerate(data[key]):
            if not isinstance(item, dict):
                raise MemorySchemaError(f"'{key}[{index}]' must be an object")

    for index, item in enumerate(data["open_questions"]):
        if not isinstance(item, str):
            raise MemorySchemaError(f"'open_questions[{index}]' must be a string")


def parse_memory_payload(raw: str) -> dict[str, Any]:
    payload = extract_json_payload(raw)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MemorySchemaError(f"Memory payload is not valid JSON: {exc}") from exc
    validate_memory_schema(data)
    return data


def _quote_lines(quotes: list[str]) -> str:
    return "\n".join(f"> {quote}" for quote in quotes)


def render_memory_markdown(memory: dict[str, Any], artwork_name: str) -> str:
    lines: list[str] = [f"# {artwork_name}", ""]

    lines.append("## Threads")
    for thread in memory["threads"]:
        label = thread.get("label", "untitled thread")
        status = thread.get("status", "unknown")
        lines.append(f"### {label} ({status})")
        for note in thread.get("notes", []):
            lines.append(f"- {note}")
        quotes = thread.get("quotes", [])
        if quotes:
            lines.append(_quote_lines(quotes))
        lines.append("")

    lines.append("## Contradictions")
    for contradiction in memory["contradictions"]:
        a = contradiction.get("a", "")
        b = contradiction.get("b", "")
        context = contradiction.get("context", "")
        lines.append(f'- "{a}" vs. "{b}"' + (f" — {context}" if context else ""))
    lines.append("")

    lines.append("## Tangents")
    for tangent in memory["tangents"]:
        quote = tangent.get("quote", "")
        relation = tangent.get("relation", "")
        lines.append(f'- "{quote}"' + (f" — {relation}" if relation else ""))
    lines.append("")

    lines.append("## Open Questions")
    for question in memory["open_questions"]:
        lines.append(f"- {question}")
    lines.append("")

    lines.append("## Anchors")
    for anchor in memory["anchors"]:
        quote = anchor.get("quote", "")
        why = anchor.get("why_it_matters", "")
        lines.append(f'- "{quote}"' + (f" — {why}" if why else ""))

    return "\n".join(lines).rstrip() + "\n"
