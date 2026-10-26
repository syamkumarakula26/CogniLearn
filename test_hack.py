import pytest
import json

def format_source_payload(sources: dict) -> str:
    """Replicates the multi-source payload aggregation in hack.py."""
    combined = []
    for s_name, content in sources.items():
        combined.append(f"=== SOURCE START: {s_name} ===\n{content}\n=== SOURCE END: {s_name} ===")
    return "\n\n".join(combined).strip()


def strip_markdown_codeblocks(raw_text: str) -> str:
    """Replicates JSON code fence stripping used for flashcard generation."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def test_source_payload_formatting():
    sample_sources = {
        "File: os_concepts.txt": "Virtual memory decouples physical addresses.",
        "Pasted Lecture Notes": "LRU page replacement replaces least recently accessed frame."
    }
    payload = format_source_payload(sample_sources)

    assert "=== SOURCE START: File: os_concepts.txt ===" in payload
    assert "=== SOURCE END: File: os_concepts.txt ===" in payload
    assert "=== SOURCE START: Pasted Lecture Notes ===" in payload
    assert "Virtual memory decouples" in payload
    assert "LRU page replacement" in payload


def test_empty_source_payload():
    assert format_source_payload({}) == ""


def test_flashcard_json_fence_stripping_and_parsing():
    raw_ai_output = """```json
    [
      {
        "source": "File: os_concepts.txt",
        "topic": "Virtual Memory",
        "question": "What is the role of the MMU?",
        "answer": "Translates virtual addresses to physical addresses."
      }
    ]
    ```"""

    cleaned = strip_markdown_codeblocks(raw_ai_output)
    parsed = json.loads(cleaned)

    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["topic"] == "Virtual Memory"
    assert "MMU" in parsed[0]["question"]


def test_flashcard_navigation_bounds():
    total_cards = 5
    card_index = 0

    # Simulate next click
    if card_index < total_cards - 1:
        card_index += 1
    assert card_index == 1

    # Simulate boundary check at end
    card_index = 4
    can_next = card_index < total_cards - 1
    assert can_next is False

    # Simulate boundary check at start
    card_index = 0
    can_prev = card_index > 0
    assert can_prev is False