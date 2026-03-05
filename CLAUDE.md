# CLAUDE.md — Shorts Factory SaaS

**Last Updated**: March 5, 2026 (v9 -- Paddle signup submitted, Terms/Privacy/Refund pages built)

---

## Purpose

Package the autonomous YouTube pipeline (from `shorts-factory/`) as a monetizable service offering. This is a separate project -- own site, own deck, own materials. Pulls stats/data from `shorts-factory/` but never modifies it.

## Deliverables

### 1. Landing Page (`index.html`) -- BUILT Mar 4
- Dark theme (#0a0a0a), blue-to-purple gradient accents
- Sections: hero, stats bar, how it works (4 steps), features (9-card grid), live results (JV + CiT cards), **live demo teaser** (animated pipeline viz + "Request Early Access" CTA), pricing (3 tiers), social proof CTA, footer
- Real stats hardcoded from production data (Mar 3 snapshots):
  - JV: 1,280 subs, 7,009 views, 24 videos
  - CiT: 30 subs, 3,696 views, 25 videos
  - Combined: 10,700+ views, 49 videos, 19 agents, $0/day LLM
- Pricing: Starter $997/mo (1 channel), Growth $1,997/mo (2 channels), Enterprise (custom)
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

## Files

| File | Purpose | Client-Facing? |
|------|---------|---------------|
| `index.html` | Landing page for GitHub Pages | Yes |
| `deck.html` | Client presentation slides | Yes |
| `saas_transformation_strategy.html` | SaaS transformation analysis (architecture, blueprint, strategy, roadmap) | No |
| `terms.html` | Terms of Service | Yes |
| `privacy.html` | Privacy Policy | Yes |
| `refund.html` | Refund Policy | Yes |
| `SAAS_DEMO.html` | Internal tech demo | No |
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

## Stats Snapshot (hardcoded in pages, Mar 3 data)

| Metric | Value |
|--------|-------|
| JV Subscribers | 1,280 |
| JV Total Views | 7,009 |
| JV Videos | 24 |
| JV Top Video | St. Regis Venice (1,619 views) |
| CiT Subscribers | 30 |
| CiT Total Views | 3,696 |
| CiT Videos | 25 |
| CiT Top Video | USA Hockey Gold (907 views) |
| Combined Views | 10,705 |
| Upload Queue | 27 videos |
| Autonomous Agents | 19 |
| Production Modules | 29 |
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
- Update stats quarterly (or when numbers change significantly)

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
| **Status** | **BLOCKED** — identity verified, bank connected, all verifications passed, but NOT accepting payments. Issue: Jordan not a Stripe-supported country, Canada setup incomplete. Need to resolve country/tax config OR switch to Paddle/Lemon Squeezy (merchant of record, no country restriction) |
| **Stripe Tax** | SKIPPED for now — $124/mo or $0.50/txn. Canadian GST/HST threshold is $30K/4 quarters. Revisit when revenue flows |

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
| 1 | ~~**Switch from Stripe to Paddle**~~ — Paddle signup submitted Mar 5. Initially rejected (missing legal pages). Resubmitted with all URLs + product description. **Allow 3 working days (by Mar 8)** | **CRITICAL** | **RESUBMITTED** — check by Mar 8 |
| 2 | Update `index.html` payment links — swap Stripe links to Paddle checkout links once approved | HIGH | BLOCKED by #1 approval |
| 3 | ~~Add Terms of Service + Privacy Policy pages~~ — `terms.html`, `privacy.html`, `refund.html` BUILT Mar 5. **Need to push to GitHub** so they're live before Paddle verifies | HIGH | **BUILT — needs git push** |
| 4 | ~~Push all new files to GitHub Pages~~ — terms, privacy, refund, footer links pushed Mar 5 (`d53356c`) | HIGH | **DONE** |
| 5 | **Git hygiene overhaul** — Set up proper git workflow: feature branches for new components, clean commit history, incremental commits at each milestone. Currently committing everything to `main` directly. | MEDIUM | PENDING |

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

## Status
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
