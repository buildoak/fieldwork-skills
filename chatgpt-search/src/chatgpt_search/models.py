"""Data models for ChatGPT conversations and messages."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    """A single message extracted from a conversation."""

    id: str
    conversation_id: str
    role: str  # user, assistant, system, tool
    content: str  # prose content (code blocks stripped)
    code: str  # extracted code blocks
    content_type: str  # text, multimodal_text, code, etc.
    model_slug: Optional[str]
    created_at: Optional[float]  # Unix timestamp
    turn_index: int  # 0-based position in linearized conversation


@dataclass
class Conversation:
    """A conversation with its metadata and messages."""

    id: str
    title: str
    created_at: Optional[float]  # Unix timestamp
    updated_at: Optional[float]
    default_model_slug: Optional[str]
    messages: list[Message] = field(default_factory=list)

    @property
    def message_count(self) -> int:
        return len(self.messages)
