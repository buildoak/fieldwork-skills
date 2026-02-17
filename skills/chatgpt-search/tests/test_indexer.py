"""Tests for the indexer."""

import sqlite3
import tempfile
from pathlib import Path

from chatgpt_search.indexer import build_index

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_FILE = FIXTURES / "sample_conversations.json"


def test_build_index_creates_db():
    """Test that build_index creates a database with tables."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        stats = build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)

        assert stats["conversation_count"] > 0
        assert stats["message_count"] > 0

        conn = sqlite3.connect(str(db_path))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "conversations" in table_names
        assert "messages" in table_names

        # Check FTS table exists
        vtables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND sql LIKE '%fts5%'"
        ).fetchall()
        # fts5 tables show up differently
        fts_check = conn.execute(
            "SELECT * FROM messages_fts LIMIT 1"
        ).fetchone()
        # Should not error

        conn.close()
    finally:
        db_path.unlink(missing_ok=True)


def test_build_index_message_count_matches():
    """Test that message count in stats matches actual rows."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        stats = build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)

        conn = sqlite3.connect(str(db_path))
        actual_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        conn.close()

        assert actual_count == stats["message_count"]
    finally:
        db_path.unlink(missing_ok=True)


def test_build_index_rebuild_is_idempotent():
    """Test that rebuilding produces the same result."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        stats1 = build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)
        stats2 = build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)

        assert stats1["conversation_count"] == stats2["conversation_count"]
        assert stats1["message_count"] == stats2["message_count"]
    finally:
        db_path.unlink(missing_ok=True)


def test_fts_index_searchable():
    """Test that the FTS index is searchable after build."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Search for something that should exist in the sample data
        results = conn.execute(
            "SELECT COUNT(*) FROM messages_fts WHERE messages_fts MATCH 'the'"
        ).fetchone()
        assert results[0] > 0, "FTS index should be searchable"

        conn.close()
    finally:
        db_path.unlink(missing_ok=True)
