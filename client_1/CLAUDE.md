# CLAUDE.md — Client 1 (Virtual Test Client)

**Last Updated**: March 3, 2026 (scaffolded)

---

## Purpose

Virtual test client for the Shorts Factory SaaS offering. This directory simulates onboarding a new client channel through the autonomous YouTube pipeline. Used to validate the productized workflow, test deliverables, and build a case study before real client acquisition.

## Client Profile

| Field | Value |
|-------|-------|
| **Client Name** | TBD (virtual) |
| **Channel Name** | TBD |
| **Niche** | TBD |
| **Voice** | TBD |
| **Tone** | TBD |
| **Upload Cadence** | TBD |
| **Content Strategy** | TBD |

## Deliverables

- [ ] Channel concept & brand identity
- [ ] Content strategy document (niche, tone, differentiation)
- [ ] Story templates (JSON format matching shorts-factory pipeline)
- [ ] Sample stories (5-10 for pilot)
- [ ] Upload schedule & queue
- [ ] Performance benchmarks (what success looks like)

## Directory Structure

```
client_1/
  CLAUDE.md          -- This file
  brief/             -- Client brief, brand docs, strategy
  stories/           -- Story JSONs (same format as shorts-factory)
  output/            -- Built MP4s (if testing locally)
  reports/           -- Performance reports, case study data
```

## Rules

- All content stays in THIS directory — never modify `shorts-factory/` from here
- Story JSONs must follow the same format as `shorts-factory/stories/` (compatible with `shorts_maker.py`)
- No YouTube tokens here — no accidental uploads
- This is a sandbox — experiment freely

## Status

- Scaffolded. Awaiting channel concept & niche selection.
