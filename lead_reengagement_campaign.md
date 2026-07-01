# Lead Re-Engagement Campaign (post-DMARC) — PREP, awaiting GO

**Goal:** re-contact the 181 shortsfactory.io form leads now that DMARC is live, to test if inbox placement (and replies) improve vs the ~2% historical baseline.

## Gate before sending
1. Wait ~2–3 days for DMARC to validate; confirm with a **mail-tester.com** score (target 9–10/10, SPF+DKIM+DMARC all green) BEFORE the first send.
2. Only start if placement looks clean.

## Cadence (Khal-set, safe)
- **5 emails/day** (slow warm-up on the fresh DMARC record).
- **Freshest leads first**: 20 (<30d) → 128 (30–90d) → 31 (>90d).
- Reply-based CTA only (ask them to reply, not click) — best deliverability during warm-up.
- ~36 days total at 5/day. Reassess after batch 1.

## Segmentation
- **Has niche (177):** VALUE-ADD copy — offer a sample in their niche.
- **No niche (~2–4):** SOFT check-in copy.
- Personalize `{first_name}` and `{niche}` per lead.

## Monitor for replies
- Watch the inbox (existing `lead_inbox_watcher` + manual-reply detection) for responses to this campaign.
- On reply → route to Khal + Sandy sales flow (send the actual sample link / answer). Track reply rate vs 2% baseline, bounces, spam complaints.

---

## COPY A — VALUE-ADD (lead HAS a niche)
**Subject:** `{first_name} — a quick Shorts sample for your {niche} idea`

Hi {first_name},

A while back you tried Shorts Factory and mentioned you were focused on **{niche}**. We've been heads-down building the engine — and your note stuck with us, so we put together a short sample in the {niche} space to show what our done-for-you setup actually produces.

Want me to send it over? Just reply "yes" and I'll drop the link — no pitch, no commitment. And if the timing's off, a quick "not now" is genuinely just as helpful.

— Sandy
Shorts Factory · shortsfactory.io

---

## COPY B — SOFT CHECK-IN (lead has NO niche)
**Subject:** `{first_name} — still exploring Shorts automation?`

Hi {first_name},

You signed up to Shorts Factory a little while back, so I wanted to check in — are you still looking at automating YouTube Shorts / faceless content?

If yes, I'm happy to show you exactly what our done-for-you engine produces (a real sample, in whatever niche you're eyeing). If it's not the right time, no worries at all — a one-word reply just tells me where you're at.

— Sandy
Shorts Factory · shortsfactory.io

---

## Notes
- From: hello@shortsfactory.io (has SPF+DKIM+DMARC).
- Keep bodies plain, single soft CTA, no ALL-CAPS / no "FREE!!!" / minimal links (one footer URL max) — protects the warm-up.
- Status field per lead updated to `reengaged_YYYYMMDD` after send (idempotent — never double-send).
