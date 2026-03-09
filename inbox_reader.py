#!/usr/bin/env python3
"""
Shorts Factory — Inbox Reader
Reads emails from hello@shortsfactory.io via IMAP.

Usage:
    python3 inbox_reader.py                    # Show latest 10 emails
    python3 inbox_reader.py --unread           # Show unread only
    python3 inbox_reader.py --count 5          # Show latest 5
    python3 inbox_reader.py --from-formspree   # Show Formspree leads only
    python3 inbox_reader.py --search "keyword" # Search emails
"""

import argparse
import email
import imaplib
import json
import os
import re
from datetime import datetime
from email.header import decode_header
from pathlib import Path

IMAP_HOST = "imap.privateemail.com"
IMAP_PORT = 993
EMAIL = os.environ.get("SF_EMAIL", "hello@shortsfactory.io")
PASSWORD = os.environ.get("SF_EMAIL_PASS", "")

SAAS_DIR = Path(__file__).parent
LEADS_FILE = SAAS_DIR / "leads.json"


def decode_str(s):
    """Decode email header string."""
    if s is None:
        return ""
    decoded = decode_header(s)
    parts = []
    for data, charset in decoded:
        if isinstance(data, bytes):
            parts.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(data)
    return " ".join(parts)


def get_body(msg):
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def parse_formspree_lead(body):
    """Parse lead data from Formspree notification email."""
    lead = {}
    for field in ["name", "email", "plan", "niche", "message"]:
        match = re.search(rf"{field}\s*[:\n]\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
        if match:
            lead[field] = match.group(1).strip()
    return lead if lead.get("email") else None


def read_inbox(unread_only=False, count=10, formspree_only=False, search_term=None):
    """Read emails from inbox."""
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=15)
    mail.login(EMAIL, PASSWORD)
    mail.select("INBOX")

    if unread_only:
        criteria = "UNSEEN"
    elif search_term:
        criteria = f'(OR SUBJECT "{search_term}" BODY "{search_term}")'
    elif formspree_only:
        criteria = '(FROM "formspree")'
    else:
        criteria = "ALL"

    status, messages = mail.search(None, criteria)
    if status != "OK":
        print("No messages found.")
        mail.logout()
        return []

    msg_ids = messages[0].split()
    if not msg_ids:
        print("No messages found.")
        mail.logout()
        return []

    # Get latest N
    msg_ids = msg_ids[-count:]

    results = []
    for mid in reversed(msg_ids):
        status, data = mail.fetch(mid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(data[0][1])
        from_addr = decode_str(msg.get("From", ""))
        subject = decode_str(msg.get("Subject", ""))
        date = decode_str(msg.get("Date", ""))
        body = get_body(msg)

        entry = {
            "id": mid.decode(),
            "from": from_addr,
            "subject": subject,
            "date": date,
            "body_preview": body[:500] if body else "",
        }

        # Check if it's a Formspree lead
        if "formspree" in from_addr.lower() or "formspree" in subject.lower():
            lead = parse_formspree_lead(body)
            if lead:
                entry["lead_data"] = lead

        results.append(entry)

    mail.logout()
    return results


def display_emails(emails):
    """Pretty-print email list."""
    for i, e in enumerate(emails):
        print(f"\n{'='*60}")
        print(f"From:    {e['from']}")
        print(f"Subject: {e['subject']}")
        print(f"Date:    {e['date']}")
        if e.get("lead_data"):
            print(f"LEAD:    {json.dumps(e['lead_data'], indent=2)}")
        print(f"---")
        print(e["body_preview"])

    print(f"\n{'='*60}")
    print(f"Total: {len(emails)} email(s)")


def main():
    parser = argparse.ArgumentParser(description="Read hello@shortsfactory.io inbox")
    parser.add_argument("--unread", action="store_true", help="Unread only")
    parser.add_argument("--count", type=int, default=10, help="Number of emails")
    parser.add_argument("--from-formspree", action="store_true", help="Formspree leads only")
    parser.add_argument("--search", help="Search keyword")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not PASSWORD:
        print("ERROR: SF_EMAIL_PASS not set. Add to ~/.zshrc")
        return

    emails = read_inbox(
        unread_only=args.unread,
        count=args.count,
        formspree_only=args.from_formspree,
        search_term=args.search,
    )

    if args.json:
        print(json.dumps(emails, indent=2))
    else:
        display_emails(emails)


if __name__ == "__main__":
    main()
