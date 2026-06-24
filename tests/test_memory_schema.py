import pytest

from memory_schema import (
    MemorySchemaError,
    parse_memory_payload,
    render_memory_markdown,
    validate_memory_schema,
)

VALID_PAYLOAD = """
{
  "source": {"filename": "drawing-of-clouds.txt", "recorded_approx": null},
  "threads": [
    {"label": "movement vs stillness", "status": "unresolved",
     "notes": ["I want them to feel like they're moving — but also frozen?"],
     "quotes": ["the lines are wiggly because they never sit still"]}
  ],
  "contradictions": [
    {"a": "it's about joy", "b": "it's kind of sad actually", "context": "said within a minute"}
  ],
  "tangents": [
    {"quote": "reminds me of being on the roof with my brother", "relation": "unclear"}
  ],
  "open_questions": ["not sure if the bottom should be darker"],
  "anchors": [
    {"quote": "I was just watching the clouds", "why_it_matters": "stated reason for the piece"}
  ]
}
"""


def test_parse_memory_payload_valid():
    memory = parse_memory_payload(VALID_PAYLOAD)
    assert memory["source"]["filename"] == "drawing-of-clouds.txt"
    assert len(memory["threads"]) == 1


def test_parse_memory_payload_strips_markdown_fences():
    fenced = f"```json\n{VALID_PAYLOAD}\n```"
    memory = parse_memory_payload(fenced)
    assert memory["source"]["filename"] == "drawing-of-clouds.txt"


def test_parse_memory_payload_invalid_json_raises():
    with pytest.raises(MemorySchemaError):
        parse_memory_payload("not json at all")


def test_validate_memory_schema_missing_key_raises():
    data = {"source": {}, "threads": [], "contradictions": [], "tangents": [], "anchors": []}
    with pytest.raises(MemorySchemaError):
        validate_memory_schema(data)


def test_validate_memory_schema_wrong_type_raises():
    data = {
        "source": {},
        "threads": "not a list",
        "contradictions": [],
        "tangents": [],
        "open_questions": [],
        "anchors": [],
    }
    with pytest.raises(MemorySchemaError):
        validate_memory_schema(data)


def test_render_memory_markdown_includes_sections():
    memory = parse_memory_payload(VALID_PAYLOAD)
    rendered = render_memory_markdown(memory, "drawing-of-clouds")

    assert rendered.startswith("# drawing-of-clouds")
    assert "## Threads" in rendered
    assert "movement vs stillness (unresolved)" in rendered
    assert "## Contradictions" in rendered
    assert "it's about joy" in rendered
    assert "## Tangents" in rendered
    assert "## Open Questions" in rendered
    assert "## Anchors" in rendered
