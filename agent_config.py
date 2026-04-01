from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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

    unknown = set(raw.keys()) - ALLOWED_AGENT_KEYS
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise AgentConfigError(f"Unknown keys in {path}: {unknown_list}")

    for required in ("role", "goal", "backstory"):
        if required not in raw:
            raise AgentConfigError(f"Missing '{required}' in {path}")

    raw.setdefault("allow_delegation", False)
    raw.setdefault("verbose", False)
    return raw
