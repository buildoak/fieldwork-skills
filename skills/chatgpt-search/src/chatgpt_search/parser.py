"""Parse ChatGPT conversations.json export into structured data."""

import json
import sys
from pathlib import Path
from typing import Iterator

from .models import Conversation, Message
from .utils import clean_text, extract_text_from_parts, separate_code


def _walk_canonical_thread(mapping: dict, current_node: str) -> list[str]:
    """Walk backward from current_node via parent pointers, then reverse.

    This produces the canonical (non-branching) conversation thread.
    ChatGPT stores conversations as trees where regenerated responses
    create branches. The canonical thread follows current_node back to root.
    """
    path = []
    node_id = current_node
    visited = set()

    while node_id and node_id not in visited:
        visited.add(node_id)
        node = mapping.get(node_id)
        if node is None:
            break
        path.append(node_id)
        node_id = node.get("parent")

    path.reverse()
    return path


def _parse_message(
    node: dict,
    conversation_id: str,
    turn_index: int,
) -> Message | None:
    """Parse a single message node into a Message object.

    Returns None if the node has no message or is a system prompt to skip.
    """
    msg = node.get("message")
    if msg is None:
        return None

    author = msg.get("author", {})
    role = author.get("role", "unknown")

    content_obj = msg.get("content", {})
    content_type = content_obj.get("content_type", "text")

    # Skip content types that don't carry useful searchable text
    if content_type in ("system_error", "thoughts", "reasoning_recap"):
        return None

    # Extract text: some content types use 'parts', others use 'text' directly
    parts = content_obj.get("parts", [])
    raw_text = extract_text_from_parts(parts)

    # Fallback: 'code', 'execution_output', 'tether_quote' store text in 'text' field
    if not raw_text.strip():
        alt_text = content_obj.get("text", "")
        if isinstance(alt_text, str):
            raw_text = alt_text

    # Skip empty messages
    if not raw_text.strip():
        return None

    # Clean text
    cleaned = clean_text(raw_text)

    # For 'code' content type, the entire text is code (not prose with code blocks)
    if content_type == "code":
        prose = ""
        code = cleaned
    else:
        # Separate code blocks from prose
        prose, code = separate_code(cleaned)

    # Get model_slug from metadata
    metadata = msg.get("metadata", {})
    model_slug = metadata.get("model_slug")

    # Get timestamp
    created_at = msg.get("create_time")

    return Message(
        id=msg.get("id", node.get("id", "")),
        conversation_id=conversation_id,
        role=role,
        content=prose,
        code=code,
        content_type=content_type,
        model_slug=model_slug,
        created_at=created_at,
        turn_index=turn_index,
    )


def parse_conversation(conv: dict) -> Conversation | None:
    """Parse a single conversation dict into a Conversation object."""
    conv_id = conv.get("conversation_id") or conv.get("id", "")
    title = conv.get("title", "Untitled")
    created_at = conv.get("create_time")
    updated_at = conv.get("update_time")
    default_model_slug = conv.get("default_model_slug")

    mapping = conv.get("mapping", {})
    current_node = conv.get("current_node")

    if not mapping or not current_node:
        return None

    # Walk the canonical thread
    thread_node_ids = _walk_canonical_thread(mapping, current_node)

    # Parse messages along the canonical thread
    messages = []
    turn_index = 0
    for node_id in thread_node_ids:
        node = mapping.get(node_id)
        if node is None:
            continue
        msg = _parse_message(node, conv_id, turn_index)
        if msg is not None:
            messages.append(msg)
            turn_index += 1

    if not messages:
        return None

    return Conversation(
        id=conv_id,
        title=title,
        created_at=created_at,
        updated_at=updated_at,
        default_model_slug=default_model_slug,
        messages=messages,
    )


def parse_export(path: Path, progress: bool = True) -> Iterator[Conversation]:
    """Parse a ChatGPT conversations.json export file.

    Yields Conversation objects. Skips conversations that fail to parse.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array at top level, got {type(data).__name__}"
        )

    total = len(data)
    parsed = 0
    skipped = 0

    for i, conv_data in enumerate(data):
        try:
            conv = parse_conversation(conv_data)
            if conv is not None:
                parsed += 1
                yield conv
            else:
                skipped += 1
        except Exception as e:
            skipped += 1
            if progress:
                print(
                    f"  Warning: skipped conversation {i}: {e}",
                    file=sys.stderr,
                )

    if progress:
        print(
            f"  Parsed {parsed}/{total} conversations ({skipped} skipped)",
            file=sys.stderr,
        )
