#!/usr/bin/env python3
"""
Lead re-engagement sender (post-DMARC warm-up campaign).
Sends the next N (default 5) freshest un-contacted leads/day with a segmented,
personalized email. Value-add copy if the lead named a niche, soft check-in if not.
Idempotent: marks status=reengaged_YYYYMMDD and never double-sends.

Usage:
  python3 reengagement_sender.py --batch 5            # send today's batch
  python3 reengagement_sender.py --batch 5 --dry-run  # preview, no send
Config comes from the campaign spec: lead_reengagement_campaign.md
"""
import os, sys, json, time, argparse, datetime, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import email_sender  # send_email(to, subject, text, html=None)

LEADS = os.path.join(HERE, "leads.json")
LOG = os.path.join(HERE, "reengagement_log.jsonl")
STOP = os.path.join(HERE, ".reengagement_STOP")

SUBJECT_A = "{first} — a quick Shorts sample for your {niche} idea"
BODY_A = """Hi {first},

A while back you tried Shorts Factory and mentioned you were focused on {niche}. We've been heads-down building the engine — and your note stuck with us, so we put together a short sample in the {niche} space to show what our done-for-you setup actually produces.

Want me to send it over? Just reply "yes" and I'll drop the link — no pitch, no commitment. And if the timing's off, a quick "not now" is genuinely just as helpful.

— Sandy
Shorts Factory · shortsfactory.io"""

SUBJECT_B = "{first} — still exploring Shorts automation?"
BODY_B = """Hi {first},

You signed up to Shorts Factory a little while back, so I wanted to check in — are you still looking at automating YouTube Shorts / faceless content?

If yes, I'm happy to show you exactly what our done-for-you engine produces (a real sample, in whatever niche you're eyeing). If it's not the right time, no worries at all — a one-word reply just tells me where you're at.

— Sandy
Shorts Factory · shortsfactory.io"""

JUNK_NAMES = {"money", "test", "asdf", "n/a", "na", "none", "-", ""}


def first_name(name):
    if not name:
        return "there"
    tok = str(name).strip().split()[0]
    if tok.lower() in JUNK_NAMES or not tok.isascii() and not any(c.isalpha() for c in tok):
        return "there"
    if tok.lower() in JUNK_NAMES:
        return "there"
    return tok[:1].upper() + tok[1:]


def valid_email(e):
    return isinstance(e, str) and "@" in e and "." in e.split("@")[-1] and " " not in e.strip()


GENERIC_NICHES = {"other", "general", "misc", "n/a", "na", "none", "-"}


def clean_niche(n):
    if not n:
        return None
    n = str(n).strip()
    if len(n) < 2 or n.lower() in JUNK_NAMES or n.lower() in GENERIC_NICHES:
        return None  # generic → fall back to soft (Copy B), no awkward "for your Other idea"
    return n


def _atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_leads():
    d = json.load(open(LEADS))
    return d if isinstance(d, list) else d.get("leads", [])


def run_batch(batch=5, dry_run=False):
    if os.path.exists(STOP):
        print("STOP flag present (.reengagement_STOP) — halting.")
        return {"halted": True}
    leads = load_leads()
    today = datetime.date.today().isoformat()
    tag = "reengaged"

    def eligible(l):
        st = str(l.get("status", "") or "")
        return valid_email(l.get("email", "")) and not st.startswith(tag)

    pending = [l for l in leads if eligible(l)]
    # freshest first
    pending.sort(key=lambda l: str(l.get("date", "")), reverse=True)
    todays = pending[:batch]
    sent, failed = [], []
    for l in todays:
        first = first_name(l.get("name"))
        niche = clean_niche(l.get("niche"))
        if niche:
            subj = SUBJECT_A.format(first=first, niche=niche)
            body = BODY_A.format(first=first, niche=niche)
            variant = "A_valueadd"
        else:
            subj = SUBJECT_B.format(first=first)
            body = BODY_B.format(first=first)
            variant = "B_soft"
        to = l["email"].strip()
        print(f"[{variant}] -> {to} | {subj}")
        if dry_run:
            continue
        try:
            email_sender.send_email(to, subj, body)
            l["status"] = f"{tag}_{today.replace('-','')}"
            notes = l.get("notes") or ""
            l["notes"] = (notes + f" | reengaged {today} ({variant})").strip(" |")
            sent.append(to)
            with open(LOG, "a") as f:
                f.write(json.dumps({"ts": datetime.datetime.now().isoformat(), "to": to,
                                    "variant": variant, "subject": subj}, ensure_ascii=False) + "\n")
            time.sleep(20)  # gentle spacing
        except Exception as e:
            failed.append((to, str(e)))
            print(f"  FAIL: {e}")
    if sent and not dry_run:
        _atomic_write(LEADS, leads)
    remaining = len([l for l in leads if eligible(l)])
    return {"sent": sent, "failed": failed, "remaining": remaining, "dry_run": dry_run}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=int(os.environ.get("REENGAGE_BATCH", "5")))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = run_batch(a.batch, a.dry_run)
    print("RESULT:", json.dumps(r, ensure_ascii=False))
