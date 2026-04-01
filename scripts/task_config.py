from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ALLOWED_TASK_KEYS = {
    "display_name",
    "style_rules",
    "output_rules",
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

    unknown = set(raw.keys()) - ALLOWED_TASK_KEYS
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise TaskConfigError(f"Unknown keys in {path}: {unknown_list}")

    for required in ("description_template", "expected_output"):
        if required not in raw:
            raise TaskConfigError(f"Missing '{required}' in {path}")

    return raw
