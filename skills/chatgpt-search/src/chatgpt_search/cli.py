"""CLI interface for chatgpt-search."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .indexer import build_index
from .searcher import (
    get_conversation,
    get_conversation_keywords,
    get_stats,
    get_top_keywords,
    search,
)
from .languages import LANGUAGE_NAMES
from .utils import format_timestamp, parse_date_filter


def _lang_display_name(code: str) -> str:
    """Format a language code for display, e.g. 'en (English)'."""
    name = LANGUAGE_NAMES.get(code, "")
    if name:
        return f"{code} ({name})"
    return code


# Default paths
DEFAULT_DB = Path.home() / ".chatgpt-search" / "index.db"
DEFAULT_EXPORT = None  # Must be provided for --rebuild


def _find_db(args_db: str | None) -> Path:
    """Resolve database path."""
    if args_db:
        return Path(args_db)
    return DEFAULT_DB


def _ensure_db_exists(db_path: Path) -> None:
    """Check that the database exists, with a helpful error if not."""
    if not db_path.exists():
        print(
            f"Error: Database not found at {db_path}\n"
            f"Run: chatgpt-search --rebuild --export /path/to/conversations.json\n"
            f"Or specify a database: chatgpt-search --db /path/to/index.db",
            file=sys.stderr,
        )
        sys.exit(1)

    conn = None
    try:
        # Open read-write without creating new files and validate SQLite parsing.
        conn = sqlite3.connect(f"file:{db_path}?mode=rw", uri=True)
        conn.execute("SELECT 1").fetchone()
    except sqlite3.DatabaseError as e:
        print(
            f"Error: File exists but is not a valid SQLite database: {db_path}\n"
            f"Rebuild the index: chatgpt-search --rebuild --export /path/to/conversations.json\n"
            f"Details: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()


def cmd_search(args: argparse.Namespace) -> None:
    """Execute a search query."""
    db_path = _find_db(args.db)
    _ensure_db_exists(db_path)

    try:
        since = parse_date_filter(args.since) if args.since else None
        until = parse_date_filter(args.until) if args.until else None
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    lang_filter = getattr(args, "lang", None)

    try:
        results = search(
            db_path=db_path,
            query=args.query,
            role=args.role,
            model=args.model,
            since=since,
            until=until,
            lang=lang_filter,
            limit=args.limit,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No results found.")
        return

    # Group results by conversation for cleaner output
    seen_convs: dict[str, list] = {}
    for r in results:
        if r.conversation_id not in seen_convs:
            seen_convs[r.conversation_id] = []
        seen_convs[r.conversation_id].append(r)

    print(f"\n{'='*70}")
    print(f"  {len(results)} results across {len(seen_convs)} conversations")
    print(f"{'='*70}\n")

    for conv_id, conv_results in seen_convs.items():
        first = conv_results[0]
        print(f"  [{first.date_str}] {first.conversation_title}")
        print(f"  ID: {conv_id[:12]}...")
        if first.model_slug:
            print(f"  Model: {first.model_slug}")
        print()

        for r in conv_results:
            role_tag = f"[{r.role}]"
            print(f"    {role_tag:12} {r.content_snippet}")
            if r.code_snippet:
                print(f"    {'':12} code: {r.code_snippet}")
            print()

        print(f"  {'─'*60}\n")


def cmd_conversation(args: argparse.Namespace) -> None:
    """Browse a full conversation."""
    db_path = _find_db(args.db)
    _ensure_db_exists(db_path)

    conv = get_conversation(db_path, args.conversation)
    if conv is None:
        print(f"Conversation not found: {args.conversation}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"  {conv.title}")
    print(f"  {conv.date_str}")
    print(f"  ID: {conv.id}")
    print(f"{'='*70}\n")

    for msg in conv.messages:
        role = msg["role"]
        content = msg["content"] or ""
        code = msg["code"] or ""
        model = msg["model_slug"]
        ts = format_timestamp(msg["created_at"])

        header = f"[{role}]"
        if model:
            header += f" ({model})"
        header += f" {ts}"

        print(f"  {header}")
        print(f"  {'─'*60}")

        if content:
            # Indent content
            for line in content.split("\n"):
                print(f"    {line}")

        if code:
            print()
            print("    ```")
            for line in code.split("\n")[:20]:  # Limit code display
                print(f"    {line}")
            if code.count("\n") > 20:
                print(f"    ... ({code.count(chr(10)) - 20} more lines)")
            print("    ```")

        print()


def cmd_rebuild(args: argparse.Namespace) -> None:
    """Rebuild the search index."""
    export_path = Path(args.export)
    if not export_path.exists():
        print(f"Error: Export file not found: {export_path}", file=sys.stderr)
        sys.exit(1)

    db_path = _find_db(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Building index from {export_path}")
    print(f"Database: {db_path}")
    print()

    try:
        stats = build_index(
            json_path=export_path,
            db_path=db_path,
            rebuild=True,
            progress=True,
        )
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in export file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nIndex built successfully:")
    print(f"  Conversations: {stats['conversation_count']}")
    print(f"  Messages: {stats['message_count']}")
    print(f"  Keywords: {stats.get('keyword_count', 0)}")
    print(f"  Duration: {stats['duration_s']}s")
    print(f"  Database: {stats['db_path']}")


def cmd_stats(args: argparse.Namespace) -> None:
    """Show corpus statistics."""
    db_path = _find_db(args.db)
    _ensure_db_exists(db_path)

    stats = get_stats(db_path)

    print(f"\n{'='*70}")
    print(f"  ChatGPT Search — Corpus Statistics")
    print(f"{'='*70}\n")

    print(f"  Conversations:  {stats.conversation_count:,}")
    print(f"  Messages:       {stats.message_count:,}")
    print(f"  Keywords:       {stats.keyword_count:,}")
    print(f"  Date range:     {stats.date_range[0]} to {stats.date_range[1]}")
    print(f"  Database size:  {stats.db_size_mb:.1f} MB")

    print(f"\n  Messages by role:")
    for role, count in stats.role_distribution.items():
        pct = count / stats.message_count * 100
        print(f"    {role:12} {count:>6,}  ({pct:.1f}%)")

    print(f"\n  Messages by model:")
    for model, count in stats.model_distribution.items():
        pct = count / stats.message_count * 100
        print(f"    {model:30} {count:>6,}  ({pct:.1f}%)")

    if stats.language_distribution:
        print(f"\n  Messages by language:")
        for lang, count in stats.language_distribution.items():
            pct = count / stats.message_count * 100
            lang_name = _lang_display_name(lang)
            print(f"    {lang_name:30} {count:>6,}  ({pct:.1f}%)")

    print(f"\n  Content types:")
    for ct, count in stats.top_content_types.items():
        print(f"    {ct:30} {count:>6,}")

    print()


def cmd_keywords(args: argparse.Namespace) -> None:
    """List keywords — top corpus keywords or keywords for a specific conversation."""
    db_path = _find_db(args.db)
    _ensure_db_exists(db_path)

    conv_id = getattr(args, "keywords_conversation", None)

    if conv_id:
        # Keywords for a specific conversation
        keywords = get_conversation_keywords(db_path, conv_id)

        if not keywords:
            print(f"No keywords found for conversation: {conv_id}")
            return

        print(f"\n{'='*70}")
        print(f"  Keywords for conversation {conv_id[:12]}...")
        print(f"{'='*70}\n")

        print(f"  {'Keyword':<40} {'Score':>8}")
        print(f"  {'─'*40} {'─'*8}")

        for kw in keywords:
            keyword = kw.keyword[:38] if len(kw.keyword) > 38 else kw.keyword
            print(f"  {keyword:<40} {kw.score:>8.4f}")

    else:
        # Top corpus keywords
        limit = getattr(args, "limit", 50)
        keywords = get_top_keywords(db_path, limit=limit)

        if not keywords:
            print("No keywords found. Rebuild the index to extract keywords.")
            return

        print(f"\n{'='*70}")
        print(f"  Top Keywords (by total TF-IDF score)")
        print(f"{'='*70}\n")

        print(f"  {'Keyword':<40} {'Score':>8}")
        print(f"  {'─'*40} {'─'*8}")

        for kw in keywords:
            keyword = kw.keyword[:38] if len(kw.keyword) > 38 else kw.keyword
            print(f"  {keyword:<40} {kw.score:>8.4f}")

    print()


def main():
    parser = argparse.ArgumentParser(
        prog="chatgpt-search",
        description="Search ChatGPT conversation exports using SQLite FTS5.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  chatgpt-search "transformer attention"
  chatgpt-search "kubernetes" --role user --since 2025-01
  chatgpt-search "pytorch" --model gpt-5
  chatgpt-search "machine learning" --lang ru
  chatgpt-search --conversation abc123
  chatgpt-search --rebuild --export ~/Downloads/conversations.json
  chatgpt-search --stats
  chatgpt-search --keywords
  chatgpt-search --keywords --keywords-conversation abc123
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"chatgpt-search {__version__}"
    )
    parser.add_argument(
        "--db",
        help=f"Path to SQLite database (default: {DEFAULT_DB})",
    )

    # Mutually exclusive modes
    group = parser.add_mutually_exclusive_group()
    group.add_argument("query", nargs="?", help="Search query (FTS5 syntax supported)")
    group.add_argument(
        "--conversation", "-c", metavar="ID", help="Browse a conversation by ID"
    )
    group.add_argument(
        "--rebuild", action="store_true", help="Rebuild the search index"
    )
    group.add_argument(
        "--stats", action="store_true", help="Show corpus statistics"
    )
    group.add_argument(
        "--keywords",
        action="store_true",
        help="List top keywords in the corpus",
    )

    # Search filters
    parser.add_argument(
        "--since", help="Filter by date (YYYY, YYYY-MM, or YYYY-MM-DD)"
    )
    parser.add_argument(
        "--until", help="Filter by date (YYYY, YYYY-MM, or YYYY-MM-DD)"
    )
    parser.add_argument(
        "--role",
        choices=["user", "assistant", "system", "tool"],
        help="Filter by message role",
    )
    parser.add_argument("--model", help="Filter by model slug (partial match)")
    parser.add_argument(
        "--lang",
        help="Filter by language (ISO 639-1 code, e.g., en, ru, zh, es)",
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=20, help="Max results (default: 20)"
    )

    # Keyword options
    parser.add_argument(
        "--keywords-conversation",
        metavar="ID",
        help="Show keywords for a specific conversation (use with --keywords)",
    )

    # Rebuild options
    parser.add_argument(
        "--export", help="Path to conversations.json (required for --rebuild)"
    )

    args = parser.parse_args()

    if args.limit <= 0:
        print("Error: --limit must be greater than 0", file=sys.stderr)
        sys.exit(1)

    if args.rebuild:
        if not args.export:
            parser.error("--rebuild requires --export /path/to/conversations.json")
        cmd_rebuild(args)
    elif args.stats:
        cmd_stats(args)
    elif args.keywords:
        cmd_keywords(args)
    elif args.conversation:
        cmd_conversation(args)
    elif args.query:
        cmd_search(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
