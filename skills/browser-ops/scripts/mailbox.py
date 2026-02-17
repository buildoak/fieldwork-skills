#!/usr/bin/env python3
"""AgentMail helper — create inboxes, poll messages, extract verification data.

Usage:
    python scripts/mailbox.py create [--username NAME] [--display-name NAME]
    python scripts/mailbox.py poll <inbox_id> [--timeout SECS]
    python scripts/mailbox.py extract <inbox_id> <message_id>
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time


def _load_api_key() -> str:
    """Load AGENTMAIL_API_KEY from environment first, then shell profile."""
    key = os.environ.get("AGENTMAIL_API_KEY")
    if key:
        return key

    # Optionally load from shell profile (for systems that export it on startup).
    for profile in ("~/.zshrc", "~/.bashrc", "~/.profile"):
        env_profile = os.path.expanduser(profile)
        if os.path.exists(env_profile):
            result = subprocess.run(
                ["bash", "-c", f"source {env_profile} && echo $AGENTMAIL_API_KEY"],
                capture_output=True,
                text=True,
            )
            key = result.stdout.strip()
            if key:
                return key

    print("Error: AGENTMAIL_API_KEY not found in environment or shell profile", file=sys.stderr)
    sys.exit(1)


def _get_client():
    """Create and return an AgentMail client."""
    from agentmail import AgentMail

    api_key = _load_api_key()
    return AgentMail(api_key=api_key)


def create_inbox(username: str | None = None, display_name: str | None = None) -> dict:
    """Create a new AgentMail inbox.

    Returns dict with 'inbox_id' (email address) and 'display_name'.
    """
    from agentmail.inboxes.client import CreateInboxRequest

    client = _get_client()

    request = CreateInboxRequest(
        username=username,
        display_name=display_name,
    )

    inbox = client.inboxes.create(request=request)
    return {
        "inbox_id": inbox.inbox_id,
        "display_name": getattr(inbox, "display_name", None),
        "created_at": str(getattr(inbox, "created_at", "")),
    }


def poll_messages(inbox_id: str, timeout: int = 120, poll_interval: int = 5) -> dict | None:
    """Poll inbox for new messages. Returns first message or None on timeout."""
    client = _get_client()
    start = time.time()

    while time.time() - start < timeout:
        messages = client.inboxes.messages.list(inbox_id=inbox_id, limit=1)
        if messages.count and messages.count > 0:
            msg = messages.messages[0]
            return {
                "message_id": msg.message_id,
                "thread_id": getattr(msg, "thread_id", None),
                "from": getattr(msg, "from_", None) or getattr(msg, "from", None),
                "subject": getattr(msg, "subject", None),
                "preview": getattr(msg, "preview", None),
                "timestamp": str(getattr(msg, "timestamp", "")),
            }
        elapsed = int(time.time() - start)
        print(f"  Polling... ({elapsed}s / {timeout}s)", file=sys.stderr)
        time.sleep(poll_interval)

    return None


def get_message(inbox_id: str, message_id: str) -> dict:
    """Get full message content."""
    client = _get_client()
    msg = client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
    return {
        "message_id": msg.message_id,
        "subject": getattr(msg, "subject", None),
        "from": getattr(msg, "from_", None) or getattr(msg, "from", None),
        "text": getattr(msg, "text", None),
        "html": getattr(msg, "html", None),
        "extracted_text": getattr(msg, "extracted_text", None),
    }


def extract_verification_link(message: dict) -> str | None:
    """Extract verification/confirmation URL from email message dict."""
    body = message.get("html") or message.get("text") or ""

    patterns = [
        r'href=["\']?(https?://[^\s"\'<>]*(?:verify|confirm|activate|token|code|validate|registration|signup|auth)[^\s"\'<>]*)',
        r'(https?://[^\s<>]*(?:verify|confirm|activate|token|code|validate|registration|signup|auth)[^\s<>]*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            url = match.group(1)
            # Clean trailing quotes/brackets
            url = url.rstrip("\"'>)")
            return url

    return None


def extract_otp(message: dict) -> str | None:
    """Extract OTP code (4-8 digits) from email message dict."""
    text = message.get("text") or message.get("extracted_text") or ""

    # Look for codes near keywords first
    keyword_pattern = r'(?:code|otp|pin|verification|confirm)\s*(?:is|:)?\s*(\d{4,8})'
    match = re.search(keyword_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Fallback: standalone 4-8 digit number
    match = re.search(r'\b(\d{4,8})\b', text)
    if match:
        return match.group(1)

    return None


def _cmd_create(args):
    result = create_inbox(username=args.username, display_name=args.display_name)
    print(json.dumps(result, indent=2))


def _cmd_poll(args):
    print(f"Polling {args.inbox_id} (timeout={args.timeout}s)...", file=sys.stderr)
    result = poll_messages(args.inbox_id, timeout=args.timeout)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No messages received within timeout.", file=sys.stderr)
        sys.exit(1)


def _cmd_extract(args):
    msg = get_message(args.inbox_id, args.message_id)
    link = extract_verification_link(msg)
    otp = extract_otp(msg)

    output = {
        "message_id": msg["message_id"],
        "subject": msg.get("subject"),
        "verification_link": link,
        "otp_code": otp,
        "has_text": bool(msg.get("text")),
        "has_html": bool(msg.get("html")),
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description="AgentMail helper for browser automation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create a new inbox")
    create_parser.add_argument("--username", help="Local part of email address")
    create_parser.add_argument("--display-name", help="Display name for inbox")

    # poll
    poll_parser = subparsers.add_parser("poll", help="Poll inbox for messages")
    poll_parser.add_argument("inbox_id", help="Inbox ID (email address)")
    poll_parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")

    # extract
    extract_parser = subparsers.add_parser("extract", help="Extract verification data from message")
    extract_parser.add_argument("inbox_id", help="Inbox ID (email address)")
    extract_parser.add_argument("message_id", help="Message ID")

    args = parser.parse_args()

    if args.command == "create":
        _cmd_create(args)
    elif args.command == "poll":
        _cmd_poll(args)
    elif args.command == "extract":
        _cmd_extract(args)


if __name__ == "__main__":
    main()
