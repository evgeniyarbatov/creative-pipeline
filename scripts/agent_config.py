from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ALLOWED_TOP_LEVEL_KEYS = {
    "agent",
    "task",
}

ALLOWED_AGENT_KEYS = {
    "role",
    "goal",
    "backstory",
    "allow_delegation",
    "verbose",
}


class AgentConfigError(ValueError):
    pass


def load_agent_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AgentConfigError(f"Agent config not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AgentConfigError(f"Agent config must be a mapping: {path}")

    if "agent" in raw or "task" in raw:
        unknown_top = set(raw.keys()) - ALLOWED_TOP_LEVEL_KEYS
        if unknown_top:
            unknown_list = ", ".join(sorted(unknown_top))
            raise AgentConfigError(f"Unknown top-level keys in {path}: {unknown_list}")
        if "agent" not in raw:
            raise AgentConfigError(f"Missing 'agent' section in {path}")
        raw = raw["agent"]
        if not isinstance(raw, dict):
            raise AgentConfigError(f"'agent' section must be a mapping: {path}")

    unknown = set(raw.keys()) - ALLOWED_AGENT_KEYS
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise AgentConfigError(f"Unknown keys in {path}: {unknown_list}")

    for required in ("role", "goal"):
        if required not in raw:
            raise AgentConfigError(f"Missing '{required}' in {path}")

    raw.setdefault("backstory", "")
    raw.setdefault("allow_delegation", False)
    raw.setdefault("verbose", False)
    return raw
