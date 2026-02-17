"""Tests for the search functionality."""

import tempfile
from pathlib import Path

from chatgpt_search.indexer import build_index
from chatgpt_search.searcher import get_conversation, get_stats, search

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_FILE = FIXTURES / "sample_conversations.json"


def _build_test_db() -> Path:
    """Build a test database and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = Path(f.name)
    f.close()
    build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)
    return db_path


def test_search_returns_results():
    """Test that search returns results for a broad query."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "the")
        assert len(results) > 0
    finally:
        db_path.unlink(missing_ok=True)


def test_search_results_have_required_fields():
    """Test that search results have all required fields."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "the")
        for r in results:
            assert r.conversation_id
            assert r.conversation_title
            assert r.message_id
            assert r.role
            assert r.rank is not None
    finally:
        db_path.unlink(missing_ok=True)


def test_search_role_filter():
    """Test filtering by role."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "the", role="user")
        for r in results:
            assert r.role == "user"
    finally:
        db_path.unlink(missing_ok=True)


def test_search_limit():
    """Test result limit."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "the", limit=3)
        assert len(results) <= 3
    finally:
        db_path.unlink(missing_ok=True)


def test_search_no_results():
    """Test search with no matches."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "xyzzyplughthisisnotaword")
        assert len(results) == 0
    finally:
        db_path.unlink(missing_ok=True)


def test_search_phrase_query():
    """Test phrase query with quotes."""
    db_path = _build_test_db()
    try:
        # This should not raise an error
        results = search(db_path, '"the"')
        # May or may not find results, but should not error
    finally:
        db_path.unlink(missing_ok=True)


def test_get_conversation_by_id():
    """Test getting a full conversation."""
    db_path = _build_test_db()
    try:
        stats = get_stats(db_path)
        # Get a conversation ID from search results
        results = search(db_path, "the", limit=1)
        if results:
            conv = get_conversation(db_path, results[0].conversation_id)
            assert conv is not None
            assert conv.title
            assert len(conv.messages) > 0
    finally:
        db_path.unlink(missing_ok=True)


def test_get_conversation_not_found():
    """Test getting a non-existent conversation."""
    db_path = _build_test_db()
    try:
        conv = get_conversation(db_path, "nonexistent-id-12345")
        assert conv is None
    finally:
        db_path.unlink(missing_ok=True)


def test_get_stats():
    """Test corpus stats."""
    db_path = _build_test_db()
    try:
        stats = get_stats(db_path)
        assert stats.conversation_count > 0
        assert stats.message_count > 0
        assert stats.db_size_mb > 0
        assert len(stats.role_distribution) > 0
    finally:
        db_path.unlink(missing_ok=True)


def test_search_prefix_query():
    """Test prefix query with wildcard."""
    db_path = _build_test_db()
    try:
        results = search(db_path, "th*")
        # Should match words starting with "th"
        # May or may not have results, but should not error
    finally:
        db_path.unlink(missing_ok=True)
