"""SQLite database management — schema creation and connection handling."""

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 4

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at REAL,
    updated_at REAL,
    default_model_slug TEXT,
    message_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    code TEXT,
    content_type TEXT,
    model_slug TEXT,
    created_at REAL,
    turn_index INTEGER,
    lang TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_model ON messages(model_slug);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_lang ON messages(lang);

CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    title,
    content,
    code,
    tokenize='porter unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    score REAL NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_keywords_conversation ON keywords(conversation_id);
"""


# ---------------------------------------------------------------------------
# Migration helpers
# ---------------------------------------------------------------------------

def _get_schema_version(conn: sqlite3.Connection) -> int:
    """Get the current schema version from the meta table."""
    try:
        row = conn.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        ).fetchone()
        if row:
            return int(row[0])
    except sqlite3.OperationalError:
        pass
    return 0


def _migrate_v1_to_v2(conn: sqlite3.Connection) -> None:
    """Migrate schema from v1 to v2: add keywords table and message_count."""
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    # Ensure conversations.message_count exists when conversations table exists.
    if "conversations" in tables:
        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(conversations)").fetchall()
        ]
        if "message_count" not in columns:
            conn.execute(
                "ALTER TABLE conversations ADD COLUMN message_count INTEGER DEFAULT 0"
            )

    # Ensure keywords table/indexes exist.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            keyword TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_keywords_conversation ON keywords(conversation_id)"
    )

    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", "2"),
    )
    conn.commit()


def _migrate_v2_to_v3(conn: sqlite3.Connection) -> None:
    """Migrate schema from v2 to v3: add lang column to messages."""
    # Check if lang column already exists
    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(messages)").fetchall()
    ]
    if "lang" not in columns:
        conn.execute("ALTER TABLE messages ADD COLUMN lang TEXT")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_lang ON messages(lang)"
        )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", "3"),
    )
    conn.commit()


def _migrate_v3_to_v4(conn: sqlite3.Connection) -> None:
    """Migrate schema from v3 to v4: drop entities table (NER removed)."""
    conn.execute("DROP TABLE IF EXISTS entities")
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", "4"),
    )
    conn.commit()


def migrate_if_needed(conn: sqlite3.Connection) -> None:
    """Run any pending schema migrations."""
    version = _get_schema_version(conn)

    # Check if messages table exists (skip migration for fresh DBs)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "messages" not in tables:
        return

    if version < 2:
        _migrate_v1_to_v2(conn)
        version = 2

    if version < 3:
        _migrate_v2_to_v3(conn)
        version = 3

    if version < 4:
        _migrate_v3_to_v4(conn)



def get_connection(db_path: Path) -> sqlite3.Connection:
    """Get a SQLite connection with optimal settings for our workload."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize the database with schema. Idempotent.

    Handles migrations for existing databases:
    - v1 -> v2: add keywords table and message_count column
    - v2 -> v3: add lang column to messages
    - v3 -> v4: drop entities table (NER removed)
    """
    conn = get_connection(db_path)

    # Run migrations before schema creation (for existing DBs)
    migrate_if_needed(conn)

    conn.executescript(SCHEMA_SQL)
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", str(SCHEMA_VERSION)),
    )
    conn.commit()
    return conn


def drop_all(conn: sqlite3.Connection) -> None:
    """Drop all tables for a clean rebuild."""
    conn.executescript("""
        DROP TABLE IF EXISTS keywords;
        DROP TABLE IF EXISTS entities;  -- legacy, may not exist
        DROP TABLE IF EXISTS messages_fts;
        DROP TRIGGER IF EXISTS messages_ai;
        DROP TRIGGER IF EXISTS messages_ad;
        DROP TRIGGER IF EXISTS messages_au;
        DROP TABLE IF EXISTS messages;
        DROP TABLE IF EXISTS conversations;
        DROP TABLE IF EXISTS meta;
    """)
    conn.commit()
