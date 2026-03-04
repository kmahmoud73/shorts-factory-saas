# CLAUDE.md — Shorts Factory SaaS

**Last Updated**: March 4, 2026 (v3 -- deck slide transitions fixed, ElevenLabs TTS added to SAAS_DEMO.html, deployed to GitHub Pages at https://kmahmoud73.github.io/shorts-factory-saas/)

---

## Purpose

Package the autonomous YouTube pipeline (from `shorts-factory/`) as a monetizable service offering. This is a separate project -- own site, own deck, own materials. Pulls stats/data from `shorts-factory/` but never modifies it.

## Deliverables

### 1. Landing Page (`index.html`) -- BUILT Mar 4
- Dark theme (#0a0a0a), blue-to-purple gradient accents
- Sections: hero, stats bar, how it works (4 steps), features (9-card grid), live results (JV + CiT cards), pricing (3 tiers), social proof CTA, footer
- Real stats hardcoded from production data (Mar 3 snapshots):
  - JV: 1,280 subs, 7,009 views, 24 videos
  - CiT: 30 subs, 3,696 views, 25 videos
  - Combined: 10,700+ views, 49 videos, 19 agents, $0/day LLM
- Pricing: Starter $997/mo (1 channel), Growth $1,997/mo (2 channels), Enterprise (custom)
- Fully self-contained: inline CSS, no JS frameworks, no build tools
- Responsive (900px + 640px breakpoints)
- CTA: mailto:hello@shortsfactory.ai (placeholder)
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

### 3. SAAS_DEMO.html (pre-existing)
- Internal technical demo page (moved from shorts-factory)
- NOT client-facing

## Files

| File | Purpose | Client-Facing? |
|------|---------|---------------|
| `index.html` | Landing page for GitHub Pages | Yes |
| `deck.html` | Client presentation slides | Yes |
| `SAAS_DEMO.html` | Internal tech demo | No |
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

## Rules
- Never modify anything in `shorts-factory/`
- All output files go in THIS directory
- Client-facing only -- no internal technical details exposed
- Always update this CLAUDE.md after changes
- Update stats quarterly (or when numbers change significantly)

## GitHub Pages

**Pending setup.** To deploy:
```bash
cd /Users/digisov/Documents/shorts-factory-saas
git init
git add index.html deck.html CLAUDE.md
git commit -m "Landing page + client deck"
gh repo create shorts-factory-saas --public --source=. --push
gh api repos/digisov/shorts-factory-saas/pages -X POST -f source.branch=main -f source.path=/
```

Live URL (after setup): `https://digisov.github.io/shorts-factory-saas/`

## Client Directories

| Directory | Client | Niche | Status |
|-----------|--------|-------|--------|
| `client_1/` | Virtual test client | TBD | Scaffolded -- awaiting concept |

Each client gets their own directory with CLAUDE.md, stories, output, and reports. Story JSONs are pipeline-compatible (same format as `shorts-factory/stories/`).

## Status
- v3: Deck slide transitions fixed, ElevenLabs added to SAAS_DEMO.html (Mar 4, 2026)
- v2: Landing page + client deck BUILT (Mar 4, 2026)
- SAAS_DEMO.html moved here from shorts-factory (Mar 3)
- `client_1/` created as virtual test client sandbox (Mar 3)
- **GitHub Pages LIVE**: https://kmahmoud73.github.io/shorts-factory-saas/ (repo: kmahmoud73/shorts-factory-saas)
