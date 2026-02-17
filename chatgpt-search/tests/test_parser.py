"""Tests for the conversations.json parser."""

import json
from pathlib import Path

from chatgpt_search.parser import parse_conversation, parse_export

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_FILE = FIXTURES / "sample_conversations.json"


def _load_sample():
    with open(SAMPLE_FILE) as f:
        return json.load(f)


def test_parse_conversation_basic():
    """Test that a conversation can be parsed."""
    data = _load_sample()
    conv = parse_conversation(data[0])
    assert conv is not None
    assert conv.id
    assert conv.title
    assert len(conv.messages) > 0


def test_parse_conversation_messages_have_required_fields():
    """Test that parsed messages have all required fields."""
    data = _load_sample()
    conv = parse_conversation(data[0])
    for msg in conv.messages:
        assert msg.id
        assert msg.conversation_id == conv.id
        assert msg.role in ("user", "assistant", "system", "tool")
        assert msg.turn_index >= 0


def test_parse_conversation_turn_indices_sequential():
    """Test that turn indices are sequential."""
    data = _load_sample()
    conv = parse_conversation(data[0])
    indices = [m.turn_index for m in conv.messages]
    assert indices == list(range(len(indices)))


def test_parse_conversation_handles_branching():
    """Test that branching conversations produce a linear thread."""
    data = _load_sample()
    # Find a conversation with branching
    for conv_data in data:
        mapping = conv_data.get("mapping", {})
        has_branch = any(
            len(n.get("children", [])) > 1 for n in mapping.values()
        )
        if has_branch:
            conv = parse_conversation(conv_data)
            assert conv is not None
            # Should still produce a linear sequence
            indices = [m.turn_index for m in conv.messages]
            assert indices == list(range(len(indices)))
            return
    # If no branching conversations in sample, skip
    pass


def test_parse_export_yields_conversations():
    """Test that parse_export yields valid conversations."""
    convs = list(parse_export(SAMPLE_FILE, progress=False))
    assert len(convs) > 0
    for conv in convs:
        assert conv.id
        assert conv.title
        assert len(conv.messages) > 0


def test_parse_conversation_with_code():
    """Test that code blocks are extracted."""
    data = _load_sample()
    found_code = False
    for conv_data in data:
        conv = parse_conversation(conv_data)
        if conv:
            for msg in conv.messages:
                if msg.code:
                    found_code = True
                    break
        if found_code:
            break
    # At least one conversation should have code
    assert found_code, "Expected at least one message with code blocks"


def test_parse_conversation_skips_null_messages():
    """Test that null root messages are skipped."""
    data = _load_sample()
    conv = parse_conversation(data[0])
    for msg in conv.messages:
        assert msg.content is not None or msg.code is not None


def test_parse_conversation_missing_current_node():
    """Test handling of missing current_node."""
    conv_data = {"mapping": {}, "current_node": None, "title": "Test"}
    conv = parse_conversation(conv_data)
    assert conv is None
