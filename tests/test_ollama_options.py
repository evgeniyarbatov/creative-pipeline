import sys
import types

from captions_pipeline import get_llm, ollama_options


def test_ollama_options_defaults():
    assert ollama_options() == {
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

    get_llm("llama3:latest", None)

    assert captured["model"] == "ollama/llama3:latest"
    assert captured["options"] == ollama_options()
