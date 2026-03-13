# CLAUDE.md — Shorts Factory SaaS

**Last Updated**: March 13, 2026 (v27 -- **LLM-Powered Smart Lead Replies**: `lead_responder.py` `build_reply()` now uses Claude Haiku via `llm_client.py` to generate context-aware first replies that actually read and respond to what the lead said. Template reply kept as fallback if LLM fails. Output cleanup: strips preamble, markdown hrs, placeholder signatures. Tested: Vynx "100k subs" → smart reply clarifies we grow channels with real content, not sell subs. Previous: v26 Pricing Overhaul + Ownership Messaging)

---

## Purpose

Package the autonomous YouTube pipeline (from `shorts-factory/`) as a monetizable service offering. This is a separate project -- own site, own deck, own materials. Pulls stats/data from `shorts-factory/` but never modifies it.

## Deliverables

### 1. Landing Page (`index.html`) -- BUILT Mar 4, AUTO-UPDATED weekly
- Dark theme (#0a0a0a), blue-to-purple gradient accents
- Sections: hero, stats bar, how it works (4 steps), features (9-card grid), live results (JV + CiT cards), **live demo teaser** (animated pipeline viz + "Request Early Access" CTA), pricing (3 tiers), social proof CTA, footer
- Stats auto-updated weekly via `update_site_stats.py` from live channel data
- Pricing: Starter $997/mo (1 channel, 150 img + 100 vid credits), Growth $1,997/mo (2 channels, 300+200 credits), Enterprise (custom, unlimited vault)
- Promo: "Commit 3 months, first month FREE" + cancel guarantee
- Ownership: Channel 100% client-owned, leave anytime keep everything
- No engine brand names on any client-facing page (all generic: "premium AI engines")
- Fully self-contained: inline CSS, no JS frameworks, no build tools
- Responsive (900px + 640px breakpoints)
- Payment: Starter + Growth → Stripe Payment Links (direct checkout). Enterprise → Formspree contact form
- Stripe account: `khal.mahmoud+stripe@gmail.com` (Canada, unregistered business, statement: SHORTS FACTORY)
- Formspree: `mbdanpdr` (free 50 subs/mo) — Enterprise + all non-pricing "Get Started" buttons
- Close via X, click outside, or Escape
- GitHub Pages ready

### 2. Client Presentation Deck (`deck.html`) -- BUILT Mar 4
- 9 slides with keyboard navigation (left/right arrows), click navigation, touch swipe
- Progress bar, nav dots, slide counter, keyboard hints
- Same dark theme as landing page
- Slides:
  1. Cover -- "Shorts Factory: Autonomous YouTube Production"
  2. The Problem -- 6 pain points with time estimates
  3. Our Solution -- 4-step pipeline flow diagram + feedback loop
  4. Live Results -- JV + CiT real stats + combined summary
  5. The Technology -- 19 agents, 29 modules, $0/day, 3x engagement, 4 engines, 7-day intel
  6. What You Get -- 9 deliverables grid
  7. AI Mascot -- avatar capabilities (lip-sync, brand presence, fallback, auto-overlay)
  8. Pricing -- same 3 tiers
  9. Next Steps -- 3-step onboarding + CTA
- NO script names, Claude CLI, launchd, or internal architecture details
- Fully self-contained: inline CSS/JS
- Responsive

### 3. SaaS Transformation Strategy (`saas_transformation_strategy.html`) -- BUILT Mar 4
- Comprehensive internal analysis document for SaaS platform transformation
- 4 major sections:
  1. **Current State Architecture Map** -- Full module inventory across 6 functional layers (Intelligence, Editorial, Production, Distribution, Engagement, Analytics). 29 Python modules mapped with inputs, outputs, dependencies, external APIs, decision points, fallback chains. External API map (12 services). Critical data files/state map (12+ JSON tracker files). Pipeline flow diagram
  2. **Visual Platform Blueprint** -- Wireframe-level designs for 5 platform components: real-time workflow canvas, decision audit panel, action trace (immutable log), communication audit, template manager
  3. **SaaS Transformation Strategy** -- 13-component abstraction map (TrendScanner, EditorialEngine, StoryWriter, ComplianceGate, ImageGenerator, VideoAnimator, VoiceSynthesizer, VideoComposer, AvatarEngine, Distributor, EngagementBot, AnalyticsEngine, LLMRouter). FIXED/CONFIGURABLE/PER-TENANT classification for all config values. Multi-tenant architecture (API Gateway + Job Queue + Tenant Isolation). BYOK (Bring Your Own Key) model. Marketplace model. Unit economics (90-94% gross margins). 4 Phase 1 quick wins
  4. **Roadmap** -- MVP definition, 3-phase plan (Foundation 0-3mo, Growth 3-6mo, Scale 6-12mo), 7-item risk register with severity ratings
- Dark theme matching landing page style (#0a0a0a, blue-to-purple gradients)
- Fully self-contained: inline CSS/JS, collapsible sections, color-coded badges, ASCII diagrams
- NOT client-facing -- internal strategic planning document
- Built from comprehensive read of all 29 production Python modules in `shorts-factory/`

### 4. Legal Pages -- BUILT Mar 5
- `terms.html` — Terms of Service (15 sections: eligibility, subscriptions via Paddle, AI content, YouTube compliance, acceptable use, IP, liability, termination, governing law Ontario/Canada)
- `privacy.html` — Privacy Policy (12 sections: data collected, usage table, sharing partners, security, retention, rights, cookies, international transfers)
- `refund.html` — Refund Policy (flexible tiered refund: 7 days = 100%, 14 days = 75%, 30 days = 50%. Performance guarantee: full refund if pipeline fails to deliver within 30 days)
- All 3 match dark theme, have nav bar + footer cross-links
- Required by Paddle for domain verification

### 5. SAAS_DEMO.html (pre-existing)
- Internal technical demo page (moved from shorts-factory)
- NOT client-facing

### 6. Auto-Update Stats System -- BUILT Mar 9
- `update_site_stats.py` — reads `channel_stats.json` + `cit_channel_stats.json`, regex-patches `index.html` + `deck.html` with current numbers (subs, views, videos, top performers, combined views, queue count, days since launch), then git commit + push to GitHub Pages
- CLI: `--status` (show current vs site), `--dry-run` (preview without writing)
- Launchd: `com.shortsfactory.site-stats-update` — runs **every Sunday 11:35 PM** (after channel monitors + weekly report finish)
- Logs: `/tmp/sf-site-stats-update.log`

### 7. GoatCounter Visitor Analytics -- ADDED Mar 9
- Privacy-friendly visitor tracking (no cookies, no GDPR banner needed)
- Script tag added to all 6 client-facing HTML pages (index, deck, terms, privacy, refund, onboarding)
- Dashboard: `shortsfactory.goatcounter.com` (**ACTIVE** — login: khal.mahmoud@gmail.com)
- Tracks: page views, referrers, countries, devices, browsers
- Code: `shortsfactory` (pending account creation)

## Files

| File | Purpose | Client-Facing? |
|------|---------|---------------|
| `index.html` | Landing page for GitHub Pages | Yes |
| `deck.html` | Client presentation slides | Yes |
| `saas_transformation_strategy.html` | SaaS transformation analysis (architecture, blueprint, strategy, roadmap) | No |
| `terms.html` | Terms of Service | Yes |
| `privacy.html` | Privacy Policy | Yes |
| `refund.html` | Refund Policy | Yes |
| `onboarding.html` | **Free Channel Strategy** lead magnet — intake form, timeline, SLA, tips. Submits to Formspree → hello@shortsfactory.io | Yes (LIVE) |
| `onboarding_internal.html` | Full onboarding with internal tech setup, file paths, launchd agents, JV/CiT stats | No (gitignored) |
| `multi_channel_strategy.html` | Multi-channel YouTube compliance, monetization, AdSense architecture, client setup | No (gitignored) |
| `SAAS_DEMO.html` | Internal tech demo | No |
| `update_site_stats.py` | Auto-update site stats from live channel data, commit + push | No |
| `email_sender.py` | Send emails from hello@shortsfactory.io via SMTP | No |
| `inbox_reader.py` | Read inbox via IMAP (unread, search, Formspree filter) | No |
| `lead_responder.py` | Auto-check inbox, **LLM-powered smart replies** (Claude Haiku) to new Formspree leads + WorldView camera submissions, log to leads.json. Template fallback if LLM fails. | No |
| `lead_dashboard.py` | **Lead Command Center** — FastAPI server (port 8009). Lead scoring, IMAP reply detection, stage management, email sending | No |
| `lead_dashboard.html` | Lead Command Center UI — pipeline view, YOUR TURN alerts, conversation threads, score breakdown, actions | No |
| `leads.json` | Lead tracker (gitignored) | No |
| `sent_log.json` | Sent email log (gitignored) | No |
| `.reply_cache.json` | IMAP reply scan cache, 60s TTL (gitignored) | No |
| `CNAME` | Custom domain config for GitHub Pages | No |
| `CLAUDE.md` | Project documentation | No |
| `client_1/` | Virtual test client sandbox | No |

## Data Sources (read-only from live)

| What | Where |
|------|-------|
| Channel stats (JV) | `shorts-factory/analytics/channel_stats.json` |
| Channel stats (CiT) | `shorts-factory/analytics/cit_channel_stats.json` |
| Upload queue | `shorts-factory/.trending_upload_queue.json` |
| System docs | `shorts-factory/system_docs.html` |
| Performance data | `shorts-factory/.performance_tracker.json` |
| Pipeline architecture | `shorts-factory/CLAUDE.md` |

## Stats Snapshot (auto-updated weekly via `update_site_stats.py`, Mar 8 data)

| Metric | Value |
|--------|-------|
| JV Subscribers | 1,280 |
| JV Total Views | 8,063 |
| JV Videos | 32 |
| JV Top Video | St. Regis Venice (1,625 views) |
| CiT Subscribers | 57 |
| CiT Total Views | 5,336 |
| CiT Videos | 38 |
| CiT Top Video | Bruno Mars Grammys (977 views) |
| Combined Views | 13,399 |
| Upload Queue | 15 videos |
| Autonomous Agents | 27 |
| Production Scripts | 42 |
| Daily LLM Cost | $0 |

## Team

| Person | Role | Contact |
|--------|------|---------|
| **Khal Mahmoud** | Founder, pipeline builder | khal.mahmoud@gmail.com, +962 77 500 6300 |
| **Bashir** | Co-founder, SaaS strategist | WhatsApp (VA-based, office in Jordan) |

**Bashir's contribution**: Conceived the SaaS productization idea. Wrote the "AGENT ACTIVATION: CODEBASE ANALYSIS & SAAS TRANSFORMATION STRATEGY" prompt (4-phase architecture audit) which produced `saas_transformation_strategy.html`. Active partner — plans more sit-down sessions and Zoom calls to expand.

## Rules
- Never modify anything in `shorts-factory/`
- All output files go in THIS directory
- Client-facing only -- no internal technical details exposed
- Always update this CLAUDE.md after changes
- Stats auto-update weekly via `update_site_stats.py` + launchd (`com.shortsfactory.site-stats-update`, Sundays 11:35 PM)

## Domain & Hosting

| Property | Value |
|----------|-------|
| **Domain** | `shortsfactory.io` |
| **Registrar** | Namecheap ($34.98/yr, expires Mar 4, 2027) |
| **DNS** | Namecheap BasicDNS |
| **Hosting** | GitHub Pages (free) |
| **HTTPS** | Enforced (GitHub auto-cert) |
| **Repo** | `kmahmoud73/shorts-factory-saas` |
| **Privacy** | WhoisGuard ON (personal info hidden from WHOIS) |

### DNS Records (Namecheap Advanced DNS)

| Type | Host | Value |
|------|------|-------|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `kmahmoud73.github.io` |

### Live URLs

| URL | What |
|-----|------|
| `https://shortsfactory.io` | Landing page |
| `https://shortsfactory.io/deck.html` | Client presentation deck |
| `https://www.shortsfactory.io` | Redirects to apex |
| `https://kmahmoud73.github.io/shorts-factory-saas/` | GitHub Pages fallback URL |

### Payments (Stripe)

| Property | Value |
|----------|-------|
| **Account** | `khal.mahmoud+stripe@gmail.com` |
| **Country** | Canada |
| **Business Type** | Unregistered business |
| **Statement Descriptor** | SHORTS FACTORY |
| **Starter Product** | $997 one-off — `https://buy.stripe.com/6oU00lenF6vtfDuggyfbq00` |
| **Growth Product** | $1,997 one-off (prod_U5Tk25nExApVIq) — `https://buy.stripe.com/dRm9AVdjB8DB4YQ9Safbq01` |
| **Enterprise** | Contact form (Formspree) — no Stripe link |
| **Bank Account** | RBC USA |
| **Status** | **WORKING** — identity verified, bank connected, checkout links functional. Needs Canadian tax setup (GST/HST) to fully activate. Paddle rejected (Mar 5) — Stripe is the active payment processor |
| **Stripe Tax** | SKIPPED for now — $124/mo or $0.50/txn. Canadian GST/HST threshold is $30K/4 quarters. Revisit when revenue flows |

### Visitor Analytics (GoatCounter)

| Property | Value |
|----------|-------|
| **Service** | GoatCounter (free, no cookies, GDPR-friendly) |
| **Dashboard** | `shortsfactory.goatcounter.com` (**ACTIVE**) |
| **Password** | `ShFactory2026x` |
| **API Token** | In `shorts-factory/api_keys.json` → `goatcounter.shortsfactory_token` |
| **Code** | `shortsfactory` |
| **Pages tracked** | All 6: index, deck, terms, privacy, refund, onboarding |
| **Traffic** | 8 visitors as of Mar 10 (tracking since Mar 9) |
| **Script** | `<script data-goatcounter="https://shortsfactory.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>` |

### Auto-Update Stats (launchd)

| Property | Value |
|----------|-------|
| **Script** | `update_site_stats.py` |
| **Agent** | `com.shortsfactory.site-stats-update` |
| **Schedule** | Every Sunday 11:35 PM Amman time |
| **What it does** | Reads channel JSONs → patches HTML → git commit + push |
| **Log** | `/tmp/sf-site-stats-update.log` |
| **CLI** | `--status`, `--dry-run` |

### Professional Email (Titan/Namecheap)

| Property | Value |
|----------|-------|
| **Email** | `hello@shortsfactory.io` |
| **Provider** | Namecheap Private Email (Titan) — Starter |
| **Cost** | $11.88/yr (promo MAILDEAL) → renews $14.88/yr |
| **SMTP** | `smtp.privateemail.com:465` (SSL) |
| **IMAP** | `imap.privateemail.com:993` (SSL) |
| **Storage** | 5 GB |
| **Aliases** | 10 available (0 used) |
| **Creds** | `SF_EMAIL` + `SF_EMAIL_PASS` in `~/.zshrc` |
| **Webmail** | Login via Namecheap → Private Email → LOGIN |

### Lead Auto-Responder (launchd)

| Property | Value |
|----------|-------|
| **Script** | `lead_responder.py` |
| **Agent** | `com.shortsfactory.lead-responder` |
| **Schedule** | Every 30 minutes + on load |
| **What it does** | IMAP check → parse Formspree leads → **LLM smart reply** (Haiku, falls back to template) → log to leads.json |
| **Log** | `/tmp/sf-lead-responder.log` |
| **CLI** | `--dry-run`, `--status` |

### X (Twitter) Accounts
- `@shortsfactoryio` — SaaS business account (khal.mahmoud+shortsfactory@gmail.com). Profile pic: sf_logo_v2.png. Bio set. URL: shortsfactory.io. X Developer app active (API keys in Developer Console)
- `@CaughtItTrending` — CiT channel account. Bio: "The stories everyone's talking about. Before everyone's talking them." 1 Following, 1 Follower. Joined March 2026. Links to youtube.com/@CaughtItTrend...
- `@shortsfactory` — inquiry submitted via Namecheap (pending, may not come through)

## Client Directories

| Directory | Client | Niche | Status |
|-----------|--------|-------|--------|
| `client_1/` | Virtual test client | TBD | Scaffolded -- awaiting concept |

Each client gets their own directory with CLAUDE.md, stories, output, and reports. Story JSONs are pipeline-compatible (same format as `shorts-factory/stories/`).

## TODO

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | ~~**Paddle**~~ — **REJECTED** Mar 5 ("unable to approve domain"). Stripe is working, Paddle no longer needed | ~~CRITICAL~~ | **DEAD** |
| 2 | **Stripe Canadian tax setup** — Complete GST/HST config to fully activate payments | HIGH | PENDING |
| 3 | ~~Add Terms of Service + Privacy Policy pages~~ | HIGH | **DONE** (Mar 5) |
| 4 | ~~Push all new files to GitHub Pages~~ | HIGH | **DONE** (Mar 5) |
| 5 | ~~**Auto-update site stats**~~ — `update_site_stats.py` + weekly launchd agent | HIGH | **DONE** (Mar 9) |
| 6 | ~~**GoatCounter visitor analytics**~~ — script tags on all 6 pages, account ACTIVE | HIGH | **DONE** (Mar 10) — dashboard at shortsfactory.goatcounter.com |
| 7 | **Git hygiene overhaul** — feature branches, clean commit history | MEDIUM | PENDING |
| 8 | ~~**Lead Command Center**~~ — `lead_dashboard.py` + `lead_dashboard.html`, FastAPI port 8009 | HIGH | **DONE** (Mar 12) |

### Paddle Migration Plan

**Why Paddle**: Merchant of Record — they handle global tax collection/remittance (no Stripe Tax needed). Jordan explicitly supported for sellers. 5% + $0.50 flat fee. Free ACH to RBC USA.

**Khal's situation**: Canadian non-resident living in Jordan (declared, CRA knows). Jordan address: 7 Salim Qashura St, Jubaiha, Amman 19164. Banks in USA (RBC), Canada, and Jordan. PayPal. Canadian passport (AY233494) for ID. Canadian credit cards. Canadian mailing address at lawyer's office. Canadian phone +1 514 418 5332. Paddle supports Jordan directly — use Jordan address, no need to mask location.

**Steps**:
1. Sign up at paddle.com — select "Individual" (no company registration needed)
2. Identity verification via Onfido (Canadian passport + video selfie)
3. Domain verification (submit shortsfactory.io — needs ToS + Privacy Policy pages)
4. Set up products: Starter $997/mo, Growth $1,997/mo, Enterprise (contact)
5. Configure ACH payout to RBC USA bank account (free, USD)
6. Get Paddle checkout links → replace Stripe links in `index.html`
7. Test checkout flow
8. Approval timeline: 48 hours to 1 week

**Fee comparison (per $997 transaction)**:
| Processor | Fee | Annual (10 clients) |
|-----------|-----|---------------------|
| **Paddle** | $50.35 (5.05%) | $6,042 |
| Lemon Squeezy | $70.29 (7.05%) | $8,435 |
| Gumroad | $100.20 (10.05%) | $12,024 |

**Fallback**: Lemon Squeezy (also supports Jordan, simpler signup, but 7%+ fees)

### Lead Command Center (`lead_dashboard.py` + `lead_dashboard.html`)

| Property | Value |
|----------|-------|
| **Server** | FastAPI on port 8009 |
| **URL** | `http://localhost:8009` |
| **Start** | `python3 lead_dashboard.py` |
| **Leads** | 6 real external (9 total incl. 2 internal tests + 1 spam) |
| **Scoring** | 0-100: name quality, email domain, plan tier, phone, strategy form, niche, reply status |
| **Stages** | New → Auto-Replied → Your Turn → Qualifying → Engaged → Won / Lost / Spam |
| **YOUR TURN trigger** | Lead replies to email (+40 score) OR score ≥ 70 |
| **Reply detection** | IMAP scan of inbox for emails FROM known lead addresses, cached 60s |
| **Formspree poller** | Background thread polls every 3 min, auto-ingests new leads via `lead_responder.py` |
| **Actions** | Qualify, Pass, Reply (sends email), Add Note, Move Stage, Poll Formspree |
| **Thread colors** | Purple = submission, Blue = sent, Green = received |
| **Thread expand** | Collapsible messages — 3-line preview with "Show full message" toggle |
| **Email signature** | Brand-only: "Shorts Factory / Autonomous YouTube Production / shortsfactory.io" |
| **Auto-refresh** | Every 30 seconds (with new-lead detection toast + tab flash) |
| **Data files** | `leads.json` (leads), `sent_log.json` (full bodies), `.reply_cache.json` (IMAP cache) |

## Status
- v27: **LLM-Powered Smart Lead Replies** — `lead_responder.py` `build_reply()` upgraded from hardcoded template to Claude Haiku-powered context-aware replies via `llm_client.py`. Reads lead's actual message, responds intelligently (e.g. clarifies we don't sell subs if they ask about subscriber growth). Template kept as fallback. Output cleanup strips LLM preamble/signatures. (Mar 13, 2026)
- v26: **Pricing Overhaul + Ownership Messaging** — Credit system (Starter 150+100, Growth 300+200, Enterprise Unlimited Vault). All engine brand names scrubbed from client-facing pages. "3 months, first month FREE" promo badge. Channel Ownership section (3-card grid). Guarantee bar. Updated index.html, deck.html, onboarding.html, onboarding_internal.html. Pushed to GitHub Pages. (Mar 13, 2026)
- v25: **Lead Command Center auto-flow** — Formspree background poller (3-min interval, auto-ingests + auto-replies via `lead_responder.py`). Reply cache 5min→60s. UI refresh 60s→30s. New lead toast notification + tab title flash. "Poll Formspree" button + `/api/formspree/poll` + `/api/formspree/status` endpoints. (Mar 12, 2026)
- v24: **Lead Command Center polish** — Collapsible thread messages (3-line preview + "Show full message" toggle). Full email bodies in sent_log.json (was 200 chars, rebuilt to full). Submission card enriched (form type, submitted time, auto-reply speed, waiting time). Email signature rebranded from "Khal Mahmoud" to brand-only "Shorts Factory". (Mar 12, 2026)
- v23: **Lead Command Center** — `lead_dashboard.py` (FastAPI port 8009) + `lead_dashboard.html` (dark CRM dashboard). Auto-scoring 0-100, IMAP reply detection, pipeline stages, YOUR TURN alerts, conversation threads (submission→sent→received), action buttons (Qualify/Pass/Reply/Note). 6 real leads tracked, all auto-replied, 0 replies. (Mar 12, 2026)
- v21: WoW + all-time % delta indicators on all stat numbers (green for growth, red for decline, muted for flat). Channel age "Live for X days" badge on both channel cards. `update_site_stats.py` delta regex rewritten (single-pass-per-channel, fixes HTML destruction bug). CiT social footer in `trending_uploader.py`. (Mar 11, 2026)
- v18: Onboarding split public/internal. Public reframed as free channel strategy lead magnet (hero, value props, "Get My Free Strategy Report" CTA, Formspree submit). Internal version gitignored (`onboarding_internal.html`). `multi_channel_strategy.html` also gitignored. Main site nav → "Free Strategy". (Mar 10, 2026)
- v17: `multi_channel_strategy.html` — comprehensive multi-channel YouTube compliance & monetization report. 11 sections covering Brand Accounts, AdSense consolidation, YPP, AI content policy, MCN analysis, risk factors, client onboarding SaaS model, intake form, 10 recommendations. (Mar 9, 2026)
- v16: `onboarding.html` — client onboarding process (47-question intake form, tech setup checklist, 14-day timeline, SLA, 10 recommendations). (Mar 9, 2026)
- v15: Updated deck.html (27 agents, 42 scripts, 15+ video engines via PiAPI) + saas_transformation_strategy.html (42 scripts across 6 layers). Stats snapshot updated: 27 agents, 42 scripts. (Mar 9, 2026)
- v11: GoatCounter analytics added to all 5 HTML pages (`index.html`, `deck.html`, `terms.html`, `privacy.html`, `refund.html`). Dashboard at `shortsfactory.goatcounter.com` (pending account signup). No cookies, GDPR-friendly, free tier. (Mar 9, 2026)
- v10: Auto-update stats system built. `update_site_stats.py` reads live channel JSONs, regex-patches `index.html` + `deck.html`, commits + pushes to GitHub Pages. Weekly launchd `com.shortsfactory.site-stats-update` (Sundays 11:35 PM). Stats refreshed: JV 7,009→8,063 views (+15%), CiT 30→57 subs (+90%), 3,696→5,336 views (+44%), combined 10,700→13,300+. (Mar 9, 2026)
- v9: Paddle signup submitted (Sole Trader, Jordan, historyofthings911@gmail.com). Initially rejected (missing legal pages). Built `terms.html`, `privacy.html`, `refund.html` — all live on shortsfactory.io. Refund policy: flexible tiered (7d=100%, 14d=75%, 30d=50%) + 30-day performance guarantee. Footer links added to `index.html`. Resubmitted via Typeform with all URLs + product description. Review by Mar 8. Deadline in `deadlines.json`. JV momentum: latest videos hitting 90-219 views organically. (Mar 5, 2026)
- v8: SaaS Transformation Strategy document (`saas_transformation_strategy.html`) added -- comprehensive internal analysis covering current architecture (29 modules across 6 layers), visual platform blueprint (5 wireframe designs), multi-tenant SaaS transformation strategy (13 abstract components, BYOK model, unit economics), and 3-phase roadmap with risk register. Built from full codebase read of all production Python modules. (Mar 4, 2026)
- v7: Live Demo teaser section added between Results and Pricing — animated pipeline visualization (Trend Scan → AI Script → Video Build → Live Upload → Results), "Coming Soon" badge, "Request Early Access" CTA opens form with Demo tag. Nav updated. Stripe Tax skipped (revisit when revenue flows) (Mar 4, 2026)
- v6: Stripe Payment Links for Starter ($997) + Growth ($1,997), Enterprise stays as contact form. Account: Canada, khal.mahmoud+stripe@gmail.com (Mar 4, 2026)
- v5: Contact form modal with Formspree (`mbdanpdr`), replaces all 6 mailto CTAs, auto-fills plan tier per button (Mar 4, 2026)
- v4: Custom domain `shortsfactory.io` LIVE with HTTPS, DNS configured on Namecheap BasicDNS → GitHub Pages (Mar 4, 2026)
- v3: Deck slide transitions fixed, ElevenLabs added to SAAS_DEMO.html, all references updated from .ai to .io (Mar 4, 2026)
- v2: Landing page + client deck BUILT (Mar 4, 2026)
- SAAS_DEMO.html moved here from shorts-factory (Mar 3)
- `client_1/` created as virtual test client sandbox (Mar 3)
- **Custom Domain LIVE**: https://shortsfactory.io (repo: kmahmoud73/shorts-factory-saas)
