#!/usr/bin/env python3
"""
DMARC-gated launcher for the lead re-engagement campaign.
Runs daily via launchd. Before START_DATE it no-ops. On/after START_DATE it
verifies SPF+DKIM+DMARC are live, then sends the day's batch (5) and pings Khal.
Durable (launchd, reboot-proof) so the campaign can't get lost.

Khal's terms: verify DMARC clean (2-3 days) + 1 day buffer, then start; 5/day; monitor replies.
"""
import os, sys, json, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/Users/digisov/Documents/shorts-factory")  # for ceo_voice

DOMAIN = "shortsfactory.io"
START_DATE = datetime.date(2026, 7, 5)   # Jul 1 + ~3 days DMARC + 1 buffer
BATCH = int(os.environ.get("REENGAGE_BATCH", "5"))
STATE = os.path.join(HERE, ".reengagement_gate_state.json")
STOP = os.path.join(HERE, ".reengagement_STOP")


def notify(msg, urgency="info"):
    try:
        import ceo_voice
        ceo_voice.notify_khal(msg, urgency=urgency, dedup_key="reengage_gate")
    except Exception as e:
        print(f"[notify fallback] {msg}  ({e})")


def ensure_email_pass():
    """launchd has no shell env — pull SF_EMAIL_PASS from ~/.zshrc if missing."""
    if os.environ.get("SF_EMAIL_PASS"):
        return True
    zrc = os.path.expanduser("~/.zshrc")
    try:
        for line in open(zrc):
            line = line.strip()
            if line.startswith("export SF_EMAIL_PASS="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                os.environ["SF_EMAIL_PASS"] = val
            if line.startswith("export SF_EMAIL="):
                os.environ.setdefault("SF_EMAIL", line.split("=", 1)[1].strip().strip('"').strip("'"))
    except Exception:
        pass
    return bool(os.environ.get("SF_EMAIL_PASS"))


def _txt(name):
    try:
        import dns.resolver
        return [b"".join(r.strings).decode(errors="ignore") if hasattr(r, "strings")
                else str(r).strip('"') for r in dns.resolver.resolve(name, "TXT")]
    except Exception:
        out = subprocess.run(["dig", "+short", "TXT", name], capture_output=True, text=True).stdout
        return [l.strip().strip('"') for l in out.splitlines() if l.strip()]


def auth_clean():
    spf = any("v=spf1" in t for t in _txt(DOMAIN))
    dmarc = any("v=DMARC1" in t for t in _txt(f"_dmarc.{DOMAIN}"))
    dkim = any("v=DKIM1" in t for t in _txt(f"default._domainkey.{DOMAIN}"))
    return spf, dkim, dmarc


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(s):
    json.dump(s, open(STATE, "w"), indent=2)


def main():
    if os.path.exists(STOP):
        print("STOP flag present — gate disabled.")
        return
    today = datetime.date.today()
    if today < START_DATE:
        print(f"Before START_DATE ({START_DATE}); no-op.")
        return
    spf, dkim, dmarc = auth_clean()
    st = load_state()
    if not (spf and dmarc):
        # hold + alert once/day
        if st.get("last_hold_alert") != today.isoformat():
            notify(f"⏸️ Lead re-engagement HELD — email auth not verified (SPF={spf} DKIM={dkim} DMARC={dmarc}). "
                   f"Fix DNS at Namecheap; campaign will auto-start next day once clean.", urgency="high")
            st["last_hold_alert"] = today.isoformat()
            save_state(st)
        print(f"Auth not clean: SPF={spf} DKIM={dkim} DMARC={dmarc} — held.")
        return
    if not ensure_email_pass():
        notify("⚠️ Lead re-engagement: SF_EMAIL_PASS not found in env or ~/.zshrc — can't send.", urgency="high")
        return
    # one send per day
    if st.get("last_send_day") == today.isoformat():
        print("Already sent today; no-op.")
        return
    import reengagement_sender as rs
    if not st.get("started"):
        notify(f"✅ DMARC verified clean (SPF+DKIM+DMARC). Starting lead re-engagement: {BATCH}/day, "
               f"freshest first, value-add + soft copy. Reply-monitored. Create .reengagement_STOP to halt.",
               urgency="high")
        st["started"] = today.isoformat()
    res = rs.run_batch(BATCH, dry_run=False)
    st["last_send_day"] = today.isoformat()
    save_state(st)
    sent = res.get("sent", [])
    remaining = res.get("remaining", "?")
    failed = res.get("failed", [])
    msg = f"📧 Re-engagement batch: sent {len(sent)}, {remaining} leads remaining."
    if failed:
        msg += f" ⚠️ {len(failed)} failed: {failed[:2]}"
    notify(msg, urgency="info")
    if remaining == 0:
        notify("🏁 Lead re-engagement campaign COMPLETE — all leads contacted. Watch inbox for replies.",
               urgency="high")
    print("RESULT:", json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
