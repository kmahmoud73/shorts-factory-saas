#!/usr/bin/env python3
"""
Shorts Factory — Lead Auto-Responder
Checks inbox for new Formspree leads, auto-replies, logs to leads.json.

Runs via launchd every 30 minutes.

Usage:
    python3 lead_responder.py          # Check and respond to new leads
    python3 lead_responder.py --dry-run # Preview without sending
    python3 lead_responder.py --status  # Show current leads
"""

import argparse
import email
import imaplib
import json
import os
import re
import smtplib
import ssl
from datetime import datetime
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

IMAP_HOST = "imap.privateemail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.privateemail.com"
SMTP_PORT = 465
EMAIL = os.environ.get("SF_EMAIL", "hello@shortsfactory.io")
PASSWORD = os.environ.get("SF_EMAIL_PASS", "")

BCC_ADDR = "khal.mahmoud@gmail.com"

SAAS_DIR = Path(__file__).parent
LEADS_FILE = SAAS_DIR / "leads.json"
SENT_LOG = SAAS_DIR / "sent_log.json"
LOG_FILE = Path("/tmp/sf-lead-responder.log")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_leads():
    if LEADS_FILE.exists():
        return json.loads(LEADS_FILE.read_text())
    return []


def save_leads(leads):
    LEADS_FILE.write_text(json.dumps(leads, indent=2))


def get_known_emails(leads):
    return {l.get("email", "").lower() for l in leads}


def get_known_cam_fingerprints(leads):
    """Build set of content fingerprints for anonymous camera submissions.
    Prevents the same city+country+url from being added repeatedly."""
    fps = set()
    for l in leads:
        if l.get("niche") == "camera-submission" and l.get("email") == "anonymous":
            fps.add(l.get("message", "").lower().strip())
    return fps


def decode_str(s):
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


def parse_strategy_intake(body):
    """Extract fields from Free Strategy onboarding form submissions.
    These have structured sections like '=== 1A. Business & Brand Information ==='
    and field names like 'Contact Email *: value'."""
    if "=== 1A." not in body and "Free Strategy" not in body:
        return None

    lead = {"source_type": "strategy-intake"}

    # _replyto is the most reliable email (Formspree special field)
    replyto = re.search(r"_replyto\s*:\s*\n?\s*(\S+@\S+)", body, re.IGNORECASE)
    if replyto:
        lead["email"] = replyto.group(1).strip()

    # Fallback: Contact Email *: value
    if not lead.get("email"):
        ce = re.search(r"Contact Email\s*\*?\s*:\s*(\S+@\S+)", body, re.IGNORECASE)
        if ce:
            lead["email"] = ce.group(1).strip()

    # Name
    name = re.search(r"Primary Contact Name\s*\*?\s*:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
    if name:
        lead["name"] = name.group(1).strip()

    # Company
    company = re.search(r"Company / Brand Name\s*\*?\s*:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
    if company:
        lead["company"] = company.group(1).strip()

    # Niche / Industry
    niche = re.search(r"Industry / Niche\s*\*?\s*:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
    if niche:
        lead["niche"] = niche.group(1).strip()

    # Tier
    tier = re.search(r"Subscription Tier\s*\*?\s*:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
    if tier:
        lead["plan"] = tier.group(1).strip()

    # Phone
    phone = re.search(r"Contact Phone[^:]*:\s*(\+?\d[\d\s\-]+)", body, re.IGNORECASE)
    if phone:
        lead["phone"] = phone.group(1).strip()

    # Store full form text as message
    lead["message"] = body

    return lead if lead.get("email") else None


def parse_formspree_lead(body):
    """Extract lead fields from Formspree notification (simple contact form)."""
    lead = {}
    for field in ["name", "email", "plan", "niche", "message"]:
        val = _extract_field(body, field)
        if val:
            lead[field] = val
    return lead if lead.get("email") else None


def _extract_field(body, field):
    """Extract a field value from Formspree email body (handles both formats)."""
    # Format 1: "field: value" on same line
    match = re.search(rf"{field}\s*:\s*(.+?)(?:\n|$)", body, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if val and val.lower() not in ["n/a", "none", ""] and ":" not in val.split()[0] if val.split() else True:
            return val
    # Format 2: "field:\nvalue" on next line (Formspree default)
    match = re.search(rf"{field}\s*:\s*\n+\s*(\S[^\n]*)", body, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        # Skip if the "value" is actually another field label (contains colon at end of first word)
        if val and not re.match(r'^[a-z_]+\s*:', val, re.IGNORECASE) and val.lower() not in ["n/a", "none", ""]:
            return val
    return None


def parse_camera_submission(body):
    """Extract camera submission fields from WorldView Formspree notification."""
    fields = {}
    for field in ["city", "country", "youtube_url", "email", "source"]:
        val = _extract_field(body, field)
        if val:
            fields[field] = val
    # Camera submissions must have city + youtube_url to be valid
    if fields.get("city") and fields.get("youtube_url"):
        return fields
    return None


def build_camera_reply(submission):
    """Generate thank-you reply for WorldView camera submissions."""
    city = submission.get("city", "your city")
    country = submission.get("country", "")
    location = f"{city}, {country}" if country else city

    subject = "Thanks for your WorldView camera submission!"

    body = f"""Hey there,

Thanks for submitting a live camera feed for {location} to WorldView!

We've received your submission and will review it shortly. Once verified, your camera will be added to the WorldView dashboard so people around the world can tune into {city}.

WorldView is a free, open-source global intelligence dashboard — community contributions like yours are what make it special.

You can check out the live dashboard at https://worldview.ink

Thanks for being part of the community!"""

    return subject, body


def build_strategy_reply(lead):
    """Generate reply for a Free Strategy intake form submission."""
    name = lead.get("name", "there").strip() or "there"
    company = lead.get("company", "")
    niche = lead.get("niche", "")
    plan = lead.get("plan", "")

    company_line = f" for {company}" if company else ""
    niche_line = f" in the {niche} space" if niche and niche.lower() not in ["general", "other", ""] else ""
    plan_line = f"\n\nYou selected the {plan.split('—')[0].strip()} tier" if plan else ""

    subject = "We received your Channel Strategy Request"

    body = f"""Hey {name},

Thanks for filling out the full Channel Strategy form{company_line}{niche_line}. We've received every detail.{plan_line} — great choice.

Here's what happens next:

1. I'll personally review your intake within 24 hours
2. You'll receive a custom Channel Strategy Report tailored to your niche, audience, and goals
3. We'll schedule a quick call to walk through the strategy and answer any questions

In the meantime, here are our two live channels — both fully autonomous, zero manual editing:
- Jersey Vault: https://youtube.com/@JerseyVault (1,280 subs, 8K+ views)
- Caught It Trending: https://youtube.com/@CaughtItTrending (57 subs, 5,300+ views)

If you have any questions before the report arrives, just reply to this email.

Talk soon."""

    return subject, body


def build_reply(lead):
    """Generate personalized reply for a new Shorts Factory lead (simple contact form)."""
    name = lead.get("name", "there").strip() or "there"
    niche = lead.get("niche", "")
    message = lead.get("message", "")

    # Personalize based on niche
    niche_line = ""
    if niche and niche.lower() not in ["general", "other", ""]:
        niche_line = f" Saw you're interested in {niche} content — that's right in our wheelhouse."

    # If they left a message, acknowledge it
    message_line = ""
    if message and len(message.strip()) > 5:
        message_line = f"\n\nRegarding your note — got it, and happy to discuss further."

    subject = "Thanks for your interest in Shorts Factory"

    body = f"""Hey {name},

Thanks for checking out Shorts Factory.{niche_line}{message_line}

Quick questions so I can point you in the right direction:

1. What kind of content are you looking to produce? (e.g. trending stories, sports, pop culture, music, etc.)
2. Do you already have a YouTube channel, or would this be a new launch?

Here are our two live channels for reference — both fully autonomous, zero manual editing:
- Jersey Vault: https://youtube.com/@JerseyVault (1,280 subs, 8K+ views)
- Caught It Trending: https://youtube.com/@CaughtItTrending (57 subs, 5,300+ views)

Happy to walk you through how the pipeline works and what results look like.

Looking forward to hearing from you."""

    return subject, body


def send_email(to_addr, subject, body_text):
    """Send email via SMTP."""
    signature = """
--
Shorts Factory
Autonomous YouTube Production
https://shortsfactory.io
"""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Shorts Factory <{EMAIL}>"
    msg["To"] = to_addr
    msg["Bcc"] = BCC_ADDR
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text.rstrip() + signature, "plain"))

    ctx = ssl.create_default_context()
    recipients = [to_addr, BCC_ADDR]
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

    # Log
    sent_log = []
    if SENT_LOG.exists():
        sent_log = json.loads(SENT_LOG.read_text())
    sent_log.append({
        "date": datetime.now().isoformat(),
        "to": to_addr,
        "subject": subject,
        "body_preview": body_text,
    })
    SENT_LOG.write_text(json.dumps(sent_log, indent=2))


def check_for_new_leads(dry_run=False):
    """Main loop: check inbox, find new leads, reply, log."""
    leads = load_leads()
    known_emails = get_known_emails(leads)
    known_cam_fps = get_known_cam_fingerprints(leads)
    next_id = max((l.get("id", 0) for l in leads), default=0) + 1

    # Connect to inbox
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=15)
    mail.login(EMAIL, PASSWORD)
    mail.select("INBOX")

    # Search for Formspree emails
    status, messages = mail.search(None, '(FROM "formspree")')
    if status != "OK" or not messages[0]:
        log("No Formspree emails found.")
        mail.logout()
        return 0

    msg_ids = messages[0].split()
    new_count = 0

    for mid in msg_ids:
        status, data = mail.fetch(mid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(data[0][1])
        body = get_body(msg)

        # Try parsers in priority order: camera → strategy intake → simple lead
        cam_sub = parse_camera_submission(body)
        strategy = parse_strategy_intake(body)
        lead = parse_formspree_lead(body) if not strategy else None

        if cam_sub:
            cam_email = cam_sub.get("email", "").lower()
            if cam_email and cam_email in known_emails:
                continue
            # Content-based dedup for anonymous submissions (no email)
            cam_fingerprint = f"City: {cam_sub.get('city', '')} | Country: {cam_sub.get('country', '')} | URL: {cam_sub.get('youtube_url', '')}".lower().strip()
            if not cam_email and cam_fingerprint in known_cam_fps:
                continue
            log(f"NEW CAM SUBMISSION: {cam_sub.get('city', '?')} — {cam_sub.get('youtube_url', '?')}")
            subject, reply_body = build_camera_reply(cam_sub)
            entry_email = cam_email or "anonymous"
            source = "worldview.ink"
            entry = {
                "id": next_id,
                "date": datetime.now().isoformat(),
                "name": "",
                "email": entry_email,
                "plan": "",
                "niche": "camera-submission",
                "message": f"City: {cam_sub.get('city', '')} | Country: {cam_sub.get('country', '')} | URL: {cam_sub.get('youtube_url', '')}",
                "source": source,
                "status": "new",
                "notes": "",
            }
            if cam_email:
                if dry_run:
                    log(f"[DRY RUN] Would send cam thank-you to {cam_email}")
                else:
                    try:
                        send_email(cam_email, subject, reply_body)
                        log(f"Cam thank-you sent to {cam_email}")
                        entry["status"] = "auto-replied"
                        entry["notes"] = "Camera submission — auto-reply sent."
                    except Exception as e:
                        log(f"SEND FAILED to {cam_email}: {e}")
                        entry["status"] = "reply-failed"
                        entry["notes"] = f"Camera submission — reply failed: {e}"
                known_emails.add(cam_email)
            else:
                entry["notes"] = "Camera submission — no email provided."
                known_cam_fps.add(cam_fingerprint)
            leads.append(entry)
            next_id += 1
            new_count += 1
            continue

        # Strategy intake (full onboarding form)
        if strategy:
            s_email = strategy["email"].lower()
            if s_email in known_emails:
                continue
            s_name = strategy.get("name", "?")
            s_company = strategy.get("company", "")
            log(f"NEW STRATEGY INTAKE: {s_name} <{s_email}> — {s_company} / {strategy.get('niche', '?')}")

            subject, reply_body = build_strategy_reply(strategy)
            status_val = "new"

            if dry_run:
                log(f"[DRY RUN] Would send strategy reply to {s_email}:")
                log(f"  Subject: {subject}")
                log(f"  Body preview: {reply_body[:100]}...")
            else:
                try:
                    send_email(s_email, subject, reply_body)
                    log(f"Strategy reply sent to {s_email}")
                    status_val = "auto-replied"
                except Exception as e:
                    log(f"SEND FAILED to {s_email}: {e}")
                    status_val = "reply-failed"

            leads.append({
                "id": next_id,
                "date": datetime.now().isoformat(),
                "name": strategy.get("name", ""),
                "email": s_email,
                "plan": strategy.get("plan", ""),
                "niche": strategy.get("niche", ""),
                "message": f"STRATEGY INTAKE | Company: {s_company} | Phone: {strategy.get('phone', '')}",
                "source": "shortsfactory.io",
                "status": status_val if not dry_run else "new",
                "notes": f"Full strategy form submission. {'[DRY RUN]' if dry_run else 'Strategy reply sent.'}"
            })
            known_emails.add(s_email)
            next_id += 1
            new_count += 1
            continue

        if not lead:
            continue

        lead_email = lead["email"].lower()
        if lead_email in known_emails:
            continue

        # New lead found
        log(f"NEW LEAD: {lead.get('name', '?')} <{lead_email}> — niche: {lead.get('niche', '?')}")

        # Build reply
        subject, reply_body = build_reply(lead)

        if dry_run:
            log(f"[DRY RUN] Would send to {lead_email}:")
            log(f"  Subject: {subject}")
            log(f"  Body preview: {reply_body[:100]}...")
        else:
            try:
                send_email(lead_email, subject, reply_body)
                log(f"Reply sent to {lead_email}")
                status_val = "auto-replied"
            except Exception as e:
                log(f"SEND FAILED to {lead_email}: {e}")
                status_val = "reply-failed"

        # Add to leads.json
        leads.append({
            "id": next_id,
            "date": datetime.now().isoformat(),
            "name": lead.get("name", ""),
            "email": lead_email,
            "plan": lead.get("plan", ""),
            "niche": lead.get("niche", ""),
            "message": lead.get("message", ""),
            "source": "shortsfactory.io",
            "status": status_val if not dry_run else "new",
            "notes": f"Auto-detected from Formspree. {'[DRY RUN]' if dry_run else 'Auto-reply sent.'}"
        })
        known_emails.add(lead_email)
        next_id += 1
        new_count += 1

    mail.logout()

    if not dry_run and new_count > 0:
        save_leads(leads)

    log(f"Done. {new_count} new lead(s) processed.")
    return new_count


def show_status():
    leads = load_leads()
    print(f"\n{'='*60}")
    print(f"Shorts Factory Leads — {len(leads)} total")
    print(f"{'='*60}")
    for l in leads:
        print(f"\n  #{l.get('id', '?')} | {l.get('name', '?')} <{l.get('email', '?')}>")
        print(f"     Niche: {l.get('niche', '-')} | Plan: {l.get('plan', '-')}")
        print(f"     Status: {l.get('status', '-')}")
        print(f"     Notes: {l.get('notes', '-')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Shorts Factory Lead Auto-Responder")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--status", action="store_true", help="Show current leads")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if not PASSWORD:
        log("ERROR: SF_EMAIL_PASS not set")
        return

    log("Checking for new leads...")
    check_for_new_leads(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
