from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ALLOWED_TOP_LEVEL_KEYS = {
    "agent",
    "task",
}

ALLOWED_TASK_KEYS = {
    "description_template",
    "expected_output",
}


class TaskConfigError(ValueError):
    pass


def load_task_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise TaskConfigError(f"Task config not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TaskConfigError(f"Task config must be a mapping: {path}")

    if "agent" in raw or "task" in raw:
        unknown_top = set(raw.keys()) - ALLOWED_TOP_LEVEL_KEYS
        if unknown_top:
            unknown_list = ", ".join(sorted(unknown_top))
            raise TaskConfigError(f"Unknown top-level keys in {path}: {unknown_list}")
        if "task" not in raw:
            raise TaskConfigError(f"Missing 'task' section in {path}")
        raw = raw["task"]
        if not isinstance(raw, dict):
            raise TaskConfigError(f"'task' section must be a mapping: {path}")

    unknown = set(raw.keys()) - ALLOWED_TASK_KEYS
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise TaskConfigError(f"Unknown keys in {path}: {unknown_list}")

    for required in ("description_template", "expected_output"):
        if required not in raw:
            raise TaskConfigError(f"Missing '{required}' in {path}")

    return raw
