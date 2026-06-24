import sys
import types

from extract_pipeline import derivation_options, extraction_options, get_llm


def test_extraction_options_defaults():
    assert extraction_options() == {
        "temperature": 0.7,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "num_predict": 1024,
    }


def test_derivation_options_defaults():
    assert derivation_options() == {
        "temperature": 0.4,
        "top_p": 0.85,
        "repeat_penalty": 1.15,
        "num_predict": 120,
    }


def test_get_llm_passes_options_to_crewai_llm(monkeypatch):
    captured = {}

    class FakeLLM:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    fake_module = types.ModuleType("crewai")
    fake_module.LLM = FakeLLM
    monkeypatch.setitem(sys.modules, "crewai", fake_module)

    get_llm("llama3:latest", None, extraction_options())

    assert captured["model"] == "ollama/llama3:latest"
    assert captured["extra_body"] == {"options": extraction_options()}
