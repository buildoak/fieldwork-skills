"""Text processing utilities."""

import re

# Unicode Private Use Area ranges used by ChatGPT for citation markers
_PUA_PATTERN = re.compile(r"[\ue000-\uf8ff]")

# ChatGPT citation markup: citeturn0search1, citeturn2view0, etc.
_CITETURN_PATTERN = re.compile(r"citeturn\d+\w+\d*")

# Code block extraction pattern (fenced code blocks)
_CODE_BLOCK_PATTERN = re.compile(
    r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL
)


def strip_pua(text: str) -> str:
    """Remove Unicode Private Use Area characters (citation markers)."""
    return _PUA_PATTERN.sub("", text)


def separate_code(text: str) -> tuple[str, str]:
    """Separate code blocks from prose.

    Returns:
        (prose, code) — prose with code blocks removed, and code blocks joined.
    """
    code_blocks = _CODE_BLOCK_PATTERN.findall(text)
    prose = _CODE_BLOCK_PATTERN.sub("", text).strip()
    code = "\n\n".join(block.strip() for block in code_blocks if block.strip())
    return prose, code


def extract_text_from_parts(parts: list) -> str:
    """Extract text content from a message's parts array.

    Handles:
    - String parts (most common)
    - Dict parts (multimodal — skipped, they're image pointers)
    - None parts (skip)
    """
    text_parts = []
    for part in parts:
        if isinstance(part, str):
            text_parts.append(part)
        # Dict parts are multimodal (images) — skip
        # None parts — skip
    return "\n".join(text_parts)


def strip_citeturn(text: str) -> str:
    """Remove ChatGPT citation markup (citeturn0search1, citeturn2view0, etc.)."""
    return _CITETURN_PATTERN.sub("", text)


def clean_text(text: str) -> str:
    """Full text cleaning pipeline."""
    text = strip_pua(text)
    text = strip_citeturn(text)
    # Normalize whitespace (collapse multiple newlines but preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_timestamp(ts: float | None) -> str:
    """Format a Unix timestamp for display."""
    if ts is None:
        return "unknown"
    from datetime import datetime, timezone

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M")


def parse_date_filter(date_str: str) -> float:
    """Parse a date filter string like '2025-01' or '2025-01-15' to Unix timestamp."""
    from datetime import datetime, timezone

    formats = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str!r}. Use YYYY, YYYY-MM, or YYYY-MM-DD.")


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len characters, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
