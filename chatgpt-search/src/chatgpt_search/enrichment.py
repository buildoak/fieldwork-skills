"""Enrichment layer: TF-IDF keyword extraction.

Supports 15 languages with language-specific stopword lists.
"""

import re
import sqlite3
import sys
import time
from collections import defaultdict

from .languages import (
    get_combined_stopwords,
)

# Code block pattern for stripping before TF-IDF
_CODE_BLOCK_PATTERN = re.compile(r"```(?:\w+)?\s*\n.*?```", re.DOTALL)


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks from text for cleaner TF-IDF."""
    return _CODE_BLOCK_PATTERN.sub("", text)


def _get_dominant_language(conn: sqlite3.Connection, conv_id: str) -> str:
    """Get the dominant language for a conversation (majority of messages)."""
    rows = conn.execute(
        """SELECT lang, COUNT(*) as cnt FROM messages
           WHERE conversation_id = ? AND lang IS NOT NULL
           GROUP BY lang ORDER BY cnt DESC LIMIT 1""",
        (conv_id,),
    ).fetchall()
    if rows:
        return rows[0]["lang"]
    return "en"


def _get_conversation_languages(conn: sqlite3.Connection, conv_id: str) -> set[str]:
    """Get all languages present in a conversation."""
    rows = conn.execute(
        """SELECT DISTINCT lang FROM messages
           WHERE conversation_id = ? AND lang IS NOT NULL""",
        (conv_id,),
    ).fetchall()
    return {row["lang"] for row in rows} if rows else {"en"}


def extract_keywords_tfidf(
    conn: sqlite3.Connection,
    top_n: int = 10,
    progress: bool = True,
) -> int:
    """Extract TF-IDF keywords per conversation with language-aware stopwords.

    Groups conversations by dominant language and applies appropriate stopword lists.
    For mixed-language conversations, uses combined stopwords from all detected languages.

    Returns the number of keyword entries created.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        print(
            "  Warning: scikit-learn not available. Skipping TF-IDF.",
            file=sys.stderr,
        )
        return 0

    if progress:
        print("  Running multilingual TF-IDF keyword extraction...", file=sys.stderr)

    start = time.time()

    # Fetch all messages grouped by conversation
    rows = conn.execute(
        """SELECT conversation_id, GROUP_CONCAT(content, ' ') as full_text
           FROM messages
           WHERE content IS NOT NULL AND content != ''
           GROUP BY conversation_id"""
    ).fetchall()

    if not rows:
        return 0

    conv_ids = [row["conversation_id"] for row in rows]
    texts = [_strip_code_blocks(row["full_text"] or "") for row in rows]

    # Filter out empty texts after code stripping
    valid_indices = [i for i, t in enumerate(texts) if t.strip()]
    if not valid_indices:
        return 0

    valid_conv_ids = [conv_ids[i] for i in valid_indices]
    valid_texts = [texts[i] for i in valid_indices]

    # Determine dominant language per conversation and group by language
    conv_languages: dict[str, str] = {}
    conv_all_langs: dict[str, set[str]] = {}
    for conv_id in valid_conv_ids:
        conv_languages[conv_id] = _get_dominant_language(conn, conv_id)
        conv_all_langs[conv_id] = _get_conversation_languages(conn, conv_id)

    # Group by dominant language for TF-IDF processing
    lang_groups: dict[str, list[int]] = defaultdict(list)
    for idx, conv_id in enumerate(valid_conv_ids):
        lang = conv_languages[conv_id]
        lang_groups[lang].append(idx)

    keyword_count = 0

    for lang, indices in lang_groups.items():
        if len(indices) < 2:
            # TF-IDF needs at least 2 documents; use min_df=1 for small groups
            min_df = 1
        else:
            min_df = 2

        # Build stopword list: combine stopwords from all languages in this group
        all_langs_in_group = set()
        all_langs_in_group.add(lang)
        for idx in indices:
            all_langs_in_group.update(conv_all_langs[valid_conv_ids[idx]])

        combined_stops = get_combined_stopwords(all_langs_in_group)
        stop_words_param = sorted(combined_stops) if combined_stops else "english"

        group_texts = [valid_texts[i] for i in indices]
        group_conv_ids = [valid_conv_ids[i] for i in indices]

        vectorizer = TfidfVectorizer(
            max_features=50000,
            min_df=min_df,
            max_df=0.8,
            ngram_range=(1, 2),
            stop_words=stop_words_param,
            sublinear_tf=True,
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(group_texts)
        except ValueError as e:
            if progress:
                print(
                    f"  Warning: TF-IDF failed for '{lang}' group ({e}). Skipping.",
                    file=sys.stderr,
                )
            continue

        feature_names = vectorizer.get_feature_names_out()

        for local_idx in range(len(group_conv_ids)):
            conv_id = group_conv_ids[local_idx]
            row_array = tfidf_matrix[local_idx].toarray().flatten()

            top_indices = row_array.argsort()[-top_n:][::-1]

            for feat_idx in top_indices:
                score = float(row_array[feat_idx])
                if score <= 0:
                    continue

                keyword = str(feature_names[feat_idx])
                conn.execute(
                    """INSERT INTO keywords (conversation_id, keyword, score)
                       VALUES (?, ?, ?)""",
                    (conv_id, keyword, round(score, 6)),
                )
                keyword_count += 1

        if progress:
            print(
                f"  TF-IDF: processed {len(group_conv_ids)} '{lang}' conversations...",
                file=sys.stderr,
            )

    conn.commit()

    duration = time.time() - start
    if progress:
        print(
            f"  TF-IDF complete: {keyword_count} keywords from "
            f"{len(valid_conv_ids)} conversations in {duration:.1f}s",
            file=sys.stderr,
        )

    return keyword_count
