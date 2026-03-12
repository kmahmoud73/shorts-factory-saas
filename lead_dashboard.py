#!/usr/bin/env python3
"""
Shorts Factory — Lead Command Center
FastAPI dashboard for lead qualification and pipeline management.

Usage:
    python3 lead_dashboard.py              # Start on port 8009
    python3 lead_dashboard.py --port 8010  # Custom port
"""

import argparse
import email as email_lib
import imaplib
import json
import os
import re
import smtplib
import ssl
import sys
import threading
import time
from datetime import datetime
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Lead Command Center")

SAAS_DIR = Path(__file__).parent
LEADS_FILE = SAAS_DIR / "leads.json"
SENT_LOG = SAAS_DIR / "sent_log.json"
REPLY_CACHE = SAAS_DIR / ".reply_cache.json"
DASHBOARD_HTML = SAAS_DIR / "lead_dashboard.html"

IMAP_HOST = "imap.privateemail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.privateemail.com"
SMTP_PORT = 465
EMAIL_ADDR = os.environ.get("SF_EMAIL", "hello@shortsfactory.io")
EMAIL_PASS = os.environ.get("SF_EMAIL_PASS", "")
BCC_ADDR = "khal.mahmoud@gmail.com"

# Internal/test emails to exclude from real pipeline
INTERNAL_EMAILS = {"khal.mahmoud@gmail.com", "khal_6614@hotmail.com", "anonymous"}

# Reply cache TTL (60 seconds — fast pickup of lead replies)
REPLY_CACHE_TTL = 60

# Formspree poll interval (3 minutes)
FORMSPREE_POLL_INTERVAL = 180

# Background poller state
_poller_state = {
    "last_poll": None,
    "last_new_count": 0,
    "total_new_since_start": 0,
    "running": False,
    "error": None,
}


# ===== Helpers =====

def load_leads():
    if LEADS_FILE.exists():
        return json.loads(LEADS_FILE.read_text())
    return []


def save_leads(leads):
    LEADS_FILE.write_text(json.dumps(leads, indent=2))


def load_sent_log():
    if SENT_LOG.exists():
        return json.loads(SENT_LOG.read_text())
    return []


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
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return ""


# ===== Lead Scoring (0-100) =====

def score_lead(lead):
    score = 0
    name = lead.get("name", "").strip()
    email_addr = lead.get("email", "").lower()
    plan = lead.get("plan", "")
    niche = lead.get("niche", "")
    message = lead.get("message", "")

    # Full name (+15) vs partial name (+5)
    if name and len(name) > 2:
        score += 15 if " " in name else 5

    # Email quality
    if any(d in email_addr for d in ["icloud.com", "outlook.com", "protonmail.com"]):
        score += 10
    elif ".edu" in email_addr or ".org" in email_addr:
        score += 10
    elif "gmail.com" in email_addr:
        score += 5

    # Selected specific plan tier
    if plan and "general" not in plan.lower() and plan.strip():
        score += 25

    # Phone provided
    if re.search(r"Phone:\s*\+?\d", message):
        score += 20

    # Strategy intake form
    if "STRATEGY INTAKE" in message:
        score += 30

    # Niche specificity
    good_niches = ["entertainment", "gaming", "technology", "sports", "cooking", "education"]
    if niche.lower() in good_niches:
        score += 10
    elif niche and niche.lower() not in ["other", "general", "", "camera-submission"]:
        score += 5

    # Lead has replied to us
    if lead.get("has_replied"):
        score += 40

    # Message quality (non-empty, not just timestamps)
    clean_msg = re.sub(r"Submitted \d{2}:\d{2}.*", "", message).strip()
    if len(clean_msg) > 20:
        score += 10

    return min(score, 100)


def score_label(score):
    if score >= 70:
        return "hot"
    elif score >= 40:
        return "warm"
    return "cold"


# ===== Inbox Reply Detection =====

def check_inbox_for_replies():
    """Scan inbox for emails FROM known lead addresses. Cached 5 min."""
    if REPLY_CACHE.exists():
        try:
            cache = json.loads(REPLY_CACHE.read_text())
            if time.time() - cache.get("timestamp", 0) < REPLY_CACHE_TTL:
                return cache.get("replies", {})
        except json.JSONDecodeError:
            pass

    if not EMAIL_PASS:
        return {}

    leads = load_leads()
    lead_emails = {
        l["email"].lower()
        for l in leads
        if l.get("email") and l["email"].lower() not in INTERNAL_EMAILS
    }

    replies = {}
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=15)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        mail.select("INBOX")

        for lead_email in lead_emails:
            status, messages = mail.search(None, f'(FROM "{lead_email}")')
            if status == "OK" and messages[0]:
                msg_ids = messages[0].split()
                reply_list = []
                for mid in msg_ids:
                    status, data = mail.fetch(mid, "(RFC822)")
                    if status == "OK":
                        msg = email_lib.message_from_bytes(data[0][1])
                        reply_list.append({
                            "date": decode_str(msg.get("Date", "")),
                            "subject": decode_str(msg.get("Subject", "")),
                            "body": get_body(msg)[:2000],
                        })
                if reply_list:
                    replies[lead_email] = reply_list

        mail.logout()
    except Exception as e:
        print(f"IMAP scan error: {e}")

    REPLY_CACHE.write_text(json.dumps({"timestamp": time.time(), "replies": replies}))
    return replies


# ===== Pipeline Stage Logic =====

def compute_stage(lead, has_replied=False):
    """Compute pipeline stage. Manual stage overrides auto-detection."""
    manual_stage = lead.get("stage")
    if manual_stage:
        return manual_stage

    status = lead.get("status", "new")
    if status == "spam":
        return "spam"
    if lead.get("email", "").lower() in INTERNAL_EMAILS:
        return "internal"
    if has_replied:
        return "your-turn"
    if status in ("auto-replied", "contacted"):
        return "auto-replied"
    return "new"


# ===== API Routes =====

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    if DASHBOARD_HTML.exists():
        return HTMLResponse(DASHBOARD_HTML.read_text())
    return HTMLResponse("<h1>lead_dashboard.html not found</h1>")


@app.get("/api/leads")
async def get_leads():
    leads = load_leads()
    replies = check_inbox_for_replies()
    sent_log = load_sent_log()

    enriched = []
    needs_attention = 0

    for lead in leads:
        email_lower = lead.get("email", "").lower()
        has_replied = email_lower in replies
        lead["has_replied"] = has_replied
        lead["replies"] = replies.get(email_lower, [])
        lead["score"] = score_lead(lead)
        lead["score_label"] = score_label(lead["score"])
        lead["stage"] = compute_stage(lead, has_replied)
        lead["sent_emails"] = [
            s for s in sent_log if s.get("to", "").lower() == email_lower
        ]

        # Time since submission
        try:
            dt_str = lead["date"]
            if "+" in dt_str or dt_str.endswith("Z"):
                dt_str = re.sub(r"[+-]\d{2}:\d{2}$", "", dt_str).rstrip("Z")
            submitted = datetime.fromisoformat(dt_str)
            lead["age_hours"] = round(
                (datetime.now() - submitted).total_seconds() / 3600
            )
        except Exception:
            lead["age_hours"] = 0

        lead["is_internal"] = email_lower in INTERNAL_EMAILS

        if lead["stage"] == "your-turn" and not lead["is_internal"]:
            needs_attention += 1

        enriched.append(lead)

    # Sort: your-turn first, then by score descending
    stage_order = {
        "your-turn": 0, "new": 1, "auto-replied": 2, "qualifying": 3,
        "engaged": 4, "won": 5, "lost": 6, "spam": 7, "internal": 8,
    }
    enriched.sort(key=lambda x: (stage_order.get(x["stage"], 9), -x["score"]))

    external = [l for l in enriched if not l["is_internal"]]
    return {
        "leads": enriched,
        "stats": {
            "total": len(external),
            "needs_attention": needs_attention,
            "auto_replied": len([l for l in external if l["stage"] == "auto-replied"]),
            "qualifying": len([l for l in external if l["stage"] == "qualifying"]),
            "engaged": len([l for l in external if l["stage"] == "engaged"]),
            "won": len([l for l in external if l["stage"] == "won"]),
            "lost": len([l for l in external if l["stage"] == "lost"]),
        },
    }


class StageUpdate(BaseModel):
    stage: str


@app.post("/api/leads/{lead_id}/stage")
async def update_stage(lead_id: int, update: StageUpdate):
    valid = ["new", "auto-replied", "qualifying", "engaged", "your-turn", "won", "lost", "spam"]
    if update.stage not in valid:
        raise HTTPException(400, f"Invalid stage. Must be one of: {valid}")

    leads = load_leads()
    for lead in leads:
        if lead.get("id") == lead_id:
            lead["stage"] = update.stage
            ts = datetime.now().strftime("%b %d %H:%M")
            existing_notes = lead.get("notes", "")
            lead["notes"] = f"{existing_notes}\n[{ts}] Stage changed to: {update.stage}".strip()
            save_leads(leads)
            return {"ok": True, "stage": update.stage}
    raise HTTPException(404, "Lead not found")


class NoteUpdate(BaseModel):
    note: str


@app.post("/api/leads/{lead_id}/notes")
async def add_note(lead_id: int, update: NoteUpdate):
    leads = load_leads()
    for lead in leads:
        if lead.get("id") == lead_id:
            existing = lead.get("notes", "")
            ts = datetime.now().strftime("%b %d %H:%M")
            lead["notes"] = f"{existing}\n[{ts}] {update.note}".strip()
            save_leads(leads)
            return {"ok": True}
    raise HTTPException(404, "Lead not found")


class ReplyRequest(BaseModel):
    subject: str
    body: str


@app.post("/api/leads/{lead_id}/reply")
async def send_reply(lead_id: int, req: ReplyRequest):
    if not EMAIL_PASS:
        raise HTTPException(500, "Email credentials not configured (SF_EMAIL_PASS)")

    leads = load_leads()
    lead = next((l for l in leads if l.get("id") == lead_id), None)
    if not lead:
        raise HTTPException(404, "Lead not found")

    to_addr = lead["email"]
    signature = "\n\n--\nShorts Factory\nAutonomous YouTube Production\nhttps://shortsfactory.io"

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Shorts Factory <{EMAIL_ADDR}>"
    msg["To"] = to_addr
    msg["Bcc"] = BCC_ADDR
    msg["Subject"] = req.subject
    msg.attach(MIMEText(req.body.rstrip() + signature, "plain"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15) as server:
        server.login(EMAIL_ADDR, EMAIL_PASS)
        server.sendmail(EMAIL_ADDR, [to_addr, BCC_ADDR], msg.as_string())

    # Log
    sent_log = load_sent_log()
    sent_log.append({
        "date": datetime.now().isoformat(),
        "to": to_addr,
        "subject": req.subject,
        "body_preview": req.body,
    })
    SENT_LOG.write_text(json.dumps(sent_log, indent=2))

    # Update lead
    lead["stage"] = "engaged"
    ts = datetime.now().strftime("%b %d %H:%M")
    existing_notes = lead.get("notes", "")
    lead["notes"] = f"{existing_notes}\n[{ts}] Manual reply sent: {req.subject}".strip()
    save_leads(leads)

    return {"ok": True, "sent_to": to_addr}


@app.get("/api/inbox/scan")
async def scan_inbox():
    """Force-refresh inbox scan for lead replies."""
    if REPLY_CACHE.exists():
        REPLY_CACHE.unlink()
    replies = check_inbox_for_replies()
    return {
        "replies_found": len(replies),
        "from_emails": list(replies.keys()),
    }


# ===== Formspree Background Poller =====

def _run_formspree_poll():
    """Call lead_responder.check_for_new_leads() and update poller state."""
    try:
        # Import lead_responder from same directory
        sys.path.insert(0, str(SAAS_DIR))
        from lead_responder import check_for_new_leads
        sys.path.pop(0)

        _poller_state["running"] = True
        _poller_state["error"] = None
        new_count = check_for_new_leads(dry_run=False)
        _poller_state["last_poll"] = datetime.now().isoformat()
        _poller_state["last_new_count"] = new_count
        _poller_state["total_new_since_start"] += new_count
        if new_count > 0:
            print(f"[Formspree Poller] {new_count} new lead(s) ingested")
    except Exception as e:
        _poller_state["error"] = str(e)
        print(f"[Formspree Poller] Error: {e}")
    finally:
        _poller_state["running"] = False


def _formspree_poller_loop():
    """Background thread: poll Formspree every FORMSPREE_POLL_INTERVAL seconds."""
    # Initial poll after 10s startup delay
    time.sleep(10)
    while True:
        _run_formspree_poll()
        time.sleep(FORMSPREE_POLL_INTERVAL)


@app.get("/api/formspree/poll")
async def force_formspree_poll():
    """Force an immediate Formspree poll (non-blocking — runs in thread)."""
    if _poller_state["running"]:
        return {"status": "already_running", **_poller_state}
    thread = threading.Thread(target=_run_formspree_poll, daemon=True)
    thread.start()
    return {"status": "poll_started", **_poller_state}


@app.get("/api/formspree/status")
async def formspree_status():
    """Return current poller state."""
    return _poller_state


@app.on_event("startup")
async def start_formspree_poller():
    """Start the background Formspree poller on server boot."""
    if EMAIL_PASS:
        thread = threading.Thread(target=_formspree_poller_loop, daemon=True)
        thread.start()
        print("[Formspree Poller] Background poller started (every 3 min)")
    else:
        print("[Formspree Poller] SKIPPED — SF_EMAIL_PASS not set")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8009)
    args = parser.parse_args()
    print(f"\n  Lead Command Center -> http://localhost:{args.port}\n")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
