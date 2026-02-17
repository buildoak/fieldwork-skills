"""Search the FTS5 index and return results."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .db import get_connection
from .utils import format_timestamp, truncate


@dataclass
class SearchResult:
    """A single search result."""

    conversation_id: str
    conversation_title: str
    message_id: str
    role: str
    content_snippet: str
    code_snippet: str
    model_slug: Optional[str]
    created_at: Optional[float]
    turn_index: int
    rank: float  # BM25 score (lower = more relevant)

    @property
    def date_str(self) -> str:
        return format_timestamp(self.created_at)


@dataclass
class ConversationView:
    """Full conversation for browsing."""

    id: str
    title: str
    created_at: Optional[float]
    messages: list[dict]

    @property
    def date_str(self) -> str:
        return format_timestamp(self.created_at)


@dataclass
class KeywordResult:
    """A keyword for a conversation."""

    keyword: str
    score: float


@dataclass
class CorpusStats:
    """Corpus-level statistics."""

    conversation_count: int
    message_count: int
    keyword_count: int
    date_range: tuple[str, str]
    role_distribution: dict[str, int]
    model_distribution: dict[str, int]
    top_content_types: dict[str, int]
    db_size_mb: float
    language_distribution: dict[str, int]  # lang code -> message count


def _build_search_query(
    role: Optional[str] = None,
    model: Optional[str] = None,
    since: Optional[float] = None,
    until: Optional[float] = None,
    lang: Optional[str] = None,
    limit: int = 20,
) -> tuple[str, list]:
    """Build the search SQL with optional filters.

    Returns (sql, params) where the first param slot is for the FTS query.
    """
    # BM25 weights: title=10.0, content=1.0, code=0.5
    sql = """
        SELECT
            m.conversation_id,
            c.title as conversation_title,
            m.id as message_id,
            m.role,
            m.content,
            m.code,
            m.model_slug,
            m.created_at,
            m.turn_index,
            bm25(messages_fts, 10.0, 1.0, 0.5) as rank
        FROM messages_fts
        JOIN messages m ON messages_fts.rowid = m.rowid
        JOIN conversations c ON m.conversation_id = c.id
        WHERE messages_fts MATCH ?
    """
    params: list = []  # FTS query will be inserted at position 0

    filters = []
    filter_params = []

    if role:
        filters.append("m.role = ?")
        filter_params.append(role)

    if model:
        filters.append("m.model_slug LIKE ?")
        filter_params.append(f"%{model}%")

    if since is not None:
        filters.append("m.created_at >= ?")
        filter_params.append(since)

    if until is not None:
        filters.append("m.created_at <= ?")
        filter_params.append(until)

    if lang:
        filters.append(
            """m.conversation_id IN (
                SELECT DISTINCT conversation_id FROM messages
                WHERE lang = ?
            )"""
        )
        filter_params.append(lang)

    if filters:
        sql += " AND " + " AND ".join(filters)

    sql += " ORDER BY rank LIMIT ?"
    filter_params.append(limit)

    # Combine: FTS query param + filter params
    params = filter_params

    return sql, params


def _sanitize_fts_query(query: str) -> str:
    """Sanitize a user query for FTS5 MATCH syntax.

    Handles:
    - Quoted phrases (pass through)
    - Simple terms (join with implicit AND)
    - Prefix queries (term*)
    - Special characters that conflict with FTS5 syntax
    """
    query = query.strip()
    if not query:
        return query

    # If the user already used FTS5 syntax (quotes, OR, AND, NOT, *), pass through
    fts_operators = {'"', "OR ", "AND ", "NOT ", "*", "(", ")"}
    if any(op in query for op in fts_operators):
        return query

    # Remove characters that are FTS5 operators: + - ^ : .
    import re
    cleaned = re.sub(r'[+\-^:.]', ' ', query)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned:
        # If cleaning removed everything, wrap original in quotes for literal match
        return f'"{query}"'

    # Split into terms and join with implicit AND (FTS5 default)
    terms = cleaned.split()
    return " ".join(terms)


def search(
    db_path: Path,
    query: str,
    role: Optional[str] = None,
    model: Optional[str] = None,
    since: Optional[float] = None,
    until: Optional[float] = None,
    lang: Optional[str] = None,
    limit: int = 20,
) -> list[SearchResult]:
    """Search the index and return ranked results."""
    conn = get_connection(db_path)
    try:
        fts_query = _sanitize_fts_query(query)
        sql, params = _build_search_query(role, model, since, until, lang, limit)

        # Insert FTS query as first parameter
        all_params = [fts_query] + params

        try:
            rows = conn.execute(sql, all_params).fetchall()
        except sqlite3.OperationalError as e:
            raise ValueError(
                f"Invalid search query: {query!r}. "
                f"Check FTS5 syntax (for example, unmatched quotes). Error: {e}"
            ) from e

        results = []
        for row in rows:
            results.append(
                SearchResult(
                    conversation_id=row["conversation_id"],
                    conversation_title=row["conversation_title"],
                    message_id=row["message_id"],
                    role=row["role"],
                    content_snippet=truncate(row["content"] or "", 300),
                    code_snippet=truncate(row["code"] or "", 200),
                    model_slug=row["model_slug"],
                    created_at=row["created_at"],
                    turn_index=row["turn_index"],
                    rank=row["rank"],
                )
            )

        return results
    finally:
        conn.close()


def get_conversation(db_path: Path, conversation_id: str) -> Optional[ConversationView]:
    """Get a full conversation by ID (or partial ID prefix)."""
    conn = get_connection(db_path)
    try:
        # Try exact match first, then prefix match
        row = conn.execute(
            "SELECT id, title, created_at FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()

        if row is None:
            # Try prefix match
            row = conn.execute(
                "SELECT id, title, created_at FROM conversations WHERE id LIKE ?",
                (conversation_id + "%",),
            ).fetchone()

        if row is None:
            return None

        conv_id = row["id"]
        messages = conn.execute(
            """SELECT role, content, code, model_slug, created_at, turn_index
               FROM messages
               WHERE conversation_id = ?
               ORDER BY turn_index""",
            (conv_id,),
        ).fetchall()

        return ConversationView(
            id=conv_id,
            title=row["title"],
            created_at=row["created_at"],
            messages=[dict(m) for m in messages],
        )
    finally:
        conn.close()


def get_stats(db_path: Path) -> CorpusStats:
    """Get corpus-level statistics."""
    conn = get_connection(db_path)
    try:
        conv_count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]

        # Keyword count (safe for older DBs without keywords table)
        try:
            keyword_count = conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        except Exception:
            keyword_count = 0

        date_range_row = conn.execute(
            "SELECT MIN(created_at), MAX(created_at) FROM conversations"
        ).fetchone()
        date_range = (
            format_timestamp(date_range_row[0]),
            format_timestamp(date_range_row[1]),
        )

        role_rows = conn.execute(
            "SELECT role, COUNT(*) as cnt FROM messages GROUP BY role ORDER BY cnt DESC"
        ).fetchall()
        role_distribution = {row["role"]: row["cnt"] for row in role_rows}

        model_rows = conn.execute(
            """SELECT model_slug, COUNT(*) as cnt FROM messages
               WHERE model_slug IS NOT NULL
               GROUP BY model_slug ORDER BY cnt DESC"""
        ).fetchall()
        model_distribution = {row["model_slug"]: row["cnt"] for row in model_rows}

        ct_rows = conn.execute(
            """SELECT content_type, COUNT(*) as cnt FROM messages
               GROUP BY content_type ORDER BY cnt DESC"""
        ).fetchall()
        top_content_types = {row["content_type"]: row["cnt"] for row in ct_rows}

        # Language distribution
        try:
            lang_rows = conn.execute(
                """SELECT COALESCE(lang, 'unknown') as lang, COUNT(*) as cnt
                   FROM messages
                   GROUP BY lang ORDER BY cnt DESC"""
            ).fetchall()
            language_distribution = {row["lang"]: row["cnt"] for row in lang_rows}
        except Exception:
            language_distribution = {}

        db_size = Path(db_path).stat().st_size / (1024 * 1024)

        return CorpusStats(
            conversation_count=conv_count,
            message_count=msg_count,
            keyword_count=keyword_count,
            date_range=date_range,
            role_distribution=role_distribution,
            model_distribution=model_distribution,
            top_content_types=top_content_types,
            db_size_mb=round(db_size, 2),
            language_distribution=language_distribution,
        )
    finally:
        conn.close()


def get_conversation_keywords(
    db_path: Path,
    conversation_id: str,
) -> list[KeywordResult]:
    """Get TF-IDF keywords for a specific conversation."""
    conn = get_connection(db_path)
    try:
        # Try exact match, then prefix match
        rows = conn.execute(
            """SELECT keyword, score FROM keywords
               WHERE conversation_id = ?
               ORDER BY score DESC""",
            (conversation_id,),
        ).fetchall()

        if not rows:
            # Try prefix match
            rows = conn.execute(
                """SELECT keyword, score FROM keywords
                   WHERE conversation_id LIKE ?
                   ORDER BY score DESC""",
                (conversation_id + "%",),
            ).fetchall()

        return [
            KeywordResult(keyword=row["keyword"], score=row["score"])
            for row in rows
        ]
    finally:
        conn.close()


def get_top_keywords(
    db_path: Path,
    limit: int = 50,
) -> list[KeywordResult]:
    """Get the most frequent keywords across the corpus (by sum of scores)."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """SELECT keyword, SUM(score) as total_score
               FROM keywords
               GROUP BY keyword
               ORDER BY total_score DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()

        return [
            KeywordResult(keyword=row["keyword"], score=row["total_score"])
            for row in rows
        ]
    finally:
        conn.close()
