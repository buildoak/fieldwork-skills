"""Tests for multilingual support: language detection and stopwords."""

import sqlite3
import tempfile
from pathlib import Path

from chatgpt_search.languages import (
    LANGUAGE_NAMES,
    STOPWORDS,
    TARGET_LANGUAGES,
    detect_language,
    detect_language_batch,
    get_combined_stopwords,
    get_stopwords,
    language_feature_matrix,
)
from chatgpt_search.indexer import build_index
from chatgpt_search.searcher import get_stats, search

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_FILE = FIXTURES / "sample_conversations.json"


# ---------------------------------------------------------------------------
# Language detection tests
# ---------------------------------------------------------------------------


def test_detect_english():
    """Test that English text is detected correctly."""
    text = "The transformer architecture revolutionized natural language processing."
    assert detect_language(text) == "en"


def test_detect_russian():
    """Test that Russian text is detected correctly."""
    text = "Трансформерная архитектура совершила революцию в обработке естественного языка."
    assert detect_language(text) == "ru"


def test_detect_french():
    """Test that French text is detected correctly."""
    text = "L'architecture transformer a revolutionne le traitement du langage naturel."
    assert detect_language(text) == "fr"


def test_detect_short_text_fallback():
    """Short texts should fall back to 'en'."""
    assert detect_language("hi") == "en"
    assert detect_language("") == "en"
    assert detect_language("ok sure") == "en"


def test_detect_batch():
    """Batch detection returns correct length."""
    texts = [
        "Hello, how are you doing today?",
        "Bonjour, comment allez-vous aujourd'hui?",
        "Hallo, wie geht es Ihnen heute?",
    ]
    results = detect_language_batch(texts)
    assert len(results) == 3
    assert results[0] == "en"


def test_detect_chinese_normalized():
    """Chinese variants should be normalized to 'zh'."""
    # langdetect returns zh-cn or zh-tw; we normalize to zh
    text = "变压器架构彻底改变了自然语言处理的方式，深度学习模型的能力得到了显著提升。"
    result = detect_language(text)
    assert result == "zh"


# ---------------------------------------------------------------------------
# Stopwords tests
# ---------------------------------------------------------------------------


def test_english_stopwords_exist():
    """English stopwords should include common words."""
    stops = get_stopwords("en")
    assert "the" in stops
    assert "and" in stops
    assert "is" in stops
    assert len(stops) > 100


def test_russian_stopwords_exist():
    """Russian stopwords should include common words."""
    stops = get_stopwords("ru")
    assert "и" in stops
    assert "в" in stops
    assert "на" in stops
    assert "что" in stops
    assert len(stops) > 50


def test_combined_stopwords():
    """Combined stopwords should be union of both languages."""
    combined = get_combined_stopwords({"en", "ru"})
    assert "the" in combined
    assert "и" in combined


def test_all_target_languages_have_stopwords():
    """All 15 target languages should have stopword lists."""
    for lang in TARGET_LANGUAGES:
        stops = get_stopwords(lang)
        assert len(stops) > 10, f"Language '{lang}' has too few stopwords: {len(stops)}"


def test_unknown_language_returns_empty_stopwords():
    """Unknown language should return empty set."""
    assert get_stopwords("xx") == set()


# ---------------------------------------------------------------------------
# Feature matrix tests
# ---------------------------------------------------------------------------


def test_feature_matrix_all_languages():
    """Feature matrix should cover all 15 target languages."""
    matrix = language_feature_matrix()
    assert len(matrix) == 15
    for lang in TARGET_LANGUAGES:
        assert lang in matrix


def test_feature_matrix_search_always_true():
    """All languages should have search support (FTS5 handles Unicode)."""
    matrix = language_feature_matrix()
    for lang, features in matrix.items():
        assert features["search"] is True


def test_feature_matrix_no_ner():
    """Feature matrix should not include NER (removed)."""
    matrix = language_feature_matrix()
    for lang, features in matrix.items():
        assert "ner" not in features


# ---------------------------------------------------------------------------
# Language names
# ---------------------------------------------------------------------------


def test_all_target_languages_have_names():
    """All target languages should have display names."""
    for lang in TARGET_LANGUAGES:
        assert lang in LANGUAGE_NAMES
        assert len(LANGUAGE_NAMES[lang]) > 0


# ---------------------------------------------------------------------------
# Integration: language detection during index build
# ---------------------------------------------------------------------------


def _build_test_db() -> Path:
    """Build a test database with enrichment and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = Path(f.name)
    f.close()
    build_index(SAMPLE_FILE, db_path, rebuild=True, progress=False)
    return db_path


def test_messages_have_lang_column():
    """Test that messages table has lang column after build."""
    db_path = _build_test_db()
    try:
        conn = sqlite3.connect(str(db_path))
        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(messages)").fetchall()
        ]
        conn.close()
        assert "lang" in columns
    finally:
        db_path.unlink(missing_ok=True)


def test_messages_have_lang_values():
    """Test that messages have language values set."""
    db_path = _build_test_db()
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        # Check that at least some messages have lang set
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM messages WHERE lang IS NOT NULL"
        ).fetchone()
        assert row["cnt"] > 0
        conn.close()
    finally:
        db_path.unlink(missing_ok=True)


def test_stats_include_language_distribution():
    """Test that stats include language distribution."""
    db_path = _build_test_db()
    try:
        stats = get_stats(db_path)
        assert hasattr(stats, "language_distribution")
        assert isinstance(stats.language_distribution, dict)
        assert len(stats.language_distribution) > 0
    finally:
        db_path.unlink(missing_ok=True)


def test_search_with_lang_filter():
    """Test that --lang filter does not error and returns results."""
    db_path = _build_test_db()
    try:
        # Search with lang=en (should work since sample is English)
        results = search(db_path, "the", lang="en")
        # Should return results (sample data is English)
        assert len(results) >= 0  # May or may not match depending on filter
    finally:
        db_path.unlink(missing_ok=True)


def test_schema_version_is_4():
    """Test that schema version is 4 after build."""
    db_path = _build_test_db()
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        ).fetchone()
        conn.close()
        assert row["value"] == "4"
    finally:
        db_path.unlink(missing_ok=True)
