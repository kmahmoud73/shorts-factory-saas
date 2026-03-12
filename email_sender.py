#!/usr/bin/env python3
"""
Shorts Factory — Email Sender
Sends emails from hello@shortsfactory.io via Titan SMTP.

Usage:
    python3 email_sender.py --to "name@example.com" --subject "Subject" --body "Body text"
    python3 email_sender.py --to "name@example.com" --subject "Subject" --body-file reply.txt
    python3 email_sender.py --test  # send test email to yourself
"""

import argparse
import json
import os
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SMTP_HOST = "smtp.privateemail.com"
SMTP_PORT = 465
EMAIL = os.environ.get("SF_EMAIL", "hello@shortsfactory.io")
PASSWORD = os.environ.get("SF_EMAIL_PASS", "")

BCC_ADDR = "hello@shortsfactory.io"

SAAS_DIR = Path(__file__).parent
SENT_LOG = SAAS_DIR / "sent_log.json"

SIGNATURE = """
--
Shorts Factory
Autonomous YouTube Production
https://shortsfactory.io
"""


def send_email(to_addr, subject, body_text, body_html=None):
    """Send an email and log it."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Shorts Factory <{EMAIL}>"
    msg["To"] = to_addr
    msg["Bcc"] = BCC_ADDR
    msg["Subject"] = subject

    full_text = body_text.rstrip() + SIGNATURE
    msg.attach(MIMEText(full_text, "plain"))

    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    ctx = ssl.create_default_context()
    recipients = [to_addr, BCC_ADDR]
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

    # Log sent email
    log_entry = {
        "date": datetime.now().isoformat(),
        "to": to_addr,
        "subject": subject,
        "body_preview": body_text,
    }

    sent_log = []
    if SENT_LOG.exists():
        sent_log = json.loads(SENT_LOG.read_text())
    sent_log.append(log_entry)
    SENT_LOG.write_text(json.dumps(sent_log, indent=2))

    return True


def main():
    parser = argparse.ArgumentParser(description="Send email from hello@shortsfactory.io")
    parser.add_argument("--to", help="Recipient email")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body text")
    parser.add_argument("--body-file", help="Read body from file")
    parser.add_argument("--test", action="store_true", help="Send test email to self")
    args = parser.parse_args()

    if not PASSWORD:
        print("ERROR: SF_EMAIL_PASS not set. Add to ~/.zshrc")
        return

    if args.test:
        send_email(
            EMAIL,
            "Test — Shorts Factory Email Pipeline",
            "If you're reading this, the email pipeline is working.\n\nSent automatically via email_sender.py.",
        )
        print(f"Test email sent to {EMAIL}")
        return

    if not all([args.to, args.subject]):
        parser.error("--to and --subject are required")

    body = args.body or ""
    if args.body_file:
        body = Path(args.body_file).read_text()

    if not body.strip():
        parser.error("Provide --body or --body-file")

    send_email(args.to, args.subject, body)
    print(f"Sent to {args.to}: {args.subject}")


if __name__ == "__main__":
    main()
