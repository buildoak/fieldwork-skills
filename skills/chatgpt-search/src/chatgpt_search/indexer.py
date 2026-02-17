"""Index parsed conversations into SQLite with FTS5."""

import sqlite3
import sys
import time
from pathlib import Path

from .db import drop_all, init_db
from .enrichment import extract_keywords_tfidf
from .languages import detect_language
from .models import Conversation
from .parser import parse_export


def index_conversation(conn: sqlite3.Connection, conv: Conversation) -> int:
    """Insert a single conversation and its messages into the database.

    Detects language per message and stores it in the lang column.

    Returns the number of messages inserted.
    """
    conn.execute(
        """INSERT OR REPLACE INTO conversations
           (id, title, created_at, updated_at, default_model_slug, message_count)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            conv.id,
            conv.title,
            conv.created_at,
            conv.updated_at,
            conv.default_model_slug,
            conv.message_count,
        ),
    )

    msg_count = 0
    for msg in conv.messages:
        # Detect language from message content
        lang = detect_language(msg.content or "")

        try:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO messages
                   (id, conversation_id, role, content, code, content_type,
                    model_slug, created_at, turn_index, lang)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    msg.id,
                    msg.conversation_id,
                    msg.role,
                    msg.content,
                    msg.code,
                    msg.content_type,
                    msg.model_slug,
                    msg.created_at,
                    msg.turn_index,
                    lang,
                ),
            )
            # Insert into FTS index with conversation title for boosting
            rowid = cursor.lastrowid
            conn.execute(
                """INSERT INTO messages_fts(rowid, title, content, code)
                   VALUES (?, ?, ?, ?)""",
                (rowid, conv.title, msg.content, msg.code),
            )
            msg_count += 1
        except sqlite3.IntegrityError:
            # Duplicate message ID — skip
            pass

    return msg_count


def build_index(
    json_path: Path,
    db_path: Path,
    rebuild: bool = False,
    progress: bool = True,
) -> dict:
    """Build the full search index from a conversations.json export.

    Args:
        json_path: Path to conversations.json
        db_path: Path for the SQLite database
        rebuild: If True, drop and recreate all tables
        progress: If True, print progress to stderr

    Returns:
        Stats dict with conversation_count, message_count, duration_s
    """
    start = time.time()

    if rebuild and db_path.exists():
        conn = sqlite3.connect(str(db_path))
        drop_all(conn)
        conn.close()
        if progress:
            print("  Dropped existing tables for rebuild.", file=sys.stderr)

    conn = init_db(db_path)

    if progress:
        print(f"  Parsing {json_path.name}...", file=sys.stderr)

    total_conversations = 0
    total_messages = 0

    # Use a transaction for bulk inserts
    try:
        for conv in parse_export(json_path, progress=progress):
            msg_count = index_conversation(conn, conv)
            total_conversations += 1
            total_messages += msg_count

            # Commit every 100 conversations for progress safety
            if total_conversations % 100 == 0:
                conn.commit()
                if progress:
                    print(
                        f"  Indexed {total_conversations} conversations, "
                        f"{total_messages} messages...",
                        file=sys.stderr,
                    )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    # Phase 2: Enrichment (TF-IDF keywords)
    # Re-open connection for enrichment pass
    conn = init_db(db_path)
    try:
        keyword_count = extract_keywords_tfidf(conn, progress=progress)
    except Exception as e:
        if progress:
            print(f"  Warning: Enrichment error: {e}", file=sys.stderr)
        keyword_count = 0
    finally:
        conn.close()

    duration = time.time() - start

    stats = {
        "conversation_count": total_conversations,
        "message_count": total_messages,
        "keyword_count": keyword_count,
        "duration_s": round(duration, 2),
        "db_path": str(db_path),
    }

    if progress:
        print(
            f"  Done: {total_conversations} conversations, "
            f"{total_messages} messages, "
            f"{keyword_count} keywords in {duration:.1f}s",
            file=sys.stderr,
        )

    return stats
