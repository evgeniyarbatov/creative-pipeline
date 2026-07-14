import sys
import types
from typing import Any

import pytest
from extract_pipeline import derivation_options, extraction_options, get_llm


def test_extraction_options_defaults() -> None:
    assert extraction_options() == {
        "temperature": 0.7,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "num_predict": 1024,
    }


def test_derivation_options_defaults() -> None:
    assert derivation_options() == {
        "temperature": 0.4,
        "top_p": 0.85,
        "repeat_penalty": 1.15,
        "num_predict": 120,
    }


def test_get_llm_passes_options_to_crewai_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    class FakeLLM:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

    fake_module = types.ModuleType("crewai")
    setattr(fake_module, "LLM", FakeLLM)  # noqa: B010
    monkeypatch.setitem(sys.modules, "crewai", fake_module)

    get_llm("llama3:latest", None, extraction_options())

    assert captured["model"] == "ollama/llama3:latest"
    assert captured["extra_body"] == {"options": extraction_options()}
