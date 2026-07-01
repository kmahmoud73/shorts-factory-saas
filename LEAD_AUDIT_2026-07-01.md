# Shorts Factory — Lead Audit (2026-07-01)

Diagnosing: 181 leads, ~189 auto-replies sent, near-zero engagement. (Audit run on Fable model.)

## 1. Deliverability — ✅ FULLY CORRECT (not the problem)
| Record | Status | Value |
|--------|--------|-------|
| SPF | ✅ | `v=spf1 include:spf.privateemail.com ~all` |
| DKIM | ✅ | `default._domainkey` — valid 2048-bit `v=DKIM1;k=rsa` |
| DMARC | ✅ | `v=DMARC1; p=none; rua=mailto:hello@shortsfactory.io; fo=1; adkim=r; aspf=r` |
| MX | ✅ | `mx1/mx2.privateemail.com` |

Mail auth is correct and aligned for hello@shortsfactory.io. **Proof it delivers:** 3–4 leads actually replied. Optional polish: point DMARC `rua` at a monitoring address (not the sales inbox), add Google Postmaster Tools (89% of leads are @gmail), later move `p=none`→`quarantine`.

## 2. Lead quality — real humans, WRONG audience (~90% unqualified)
Not bots (0 duplicates, organic spread Mar 9–Jul 1, no scripted bursts). Breakdown of ~181:
- **~6% disposable** (6): pomow97858@duoley.com, wihah76509@fengnu.com, xalat96553@lealking.com, kovobo1465@cosdas.com, mehoka6430@pertok.com, okojaja1@deltajohnsons.com
- **~7% garbage/tests** (~12): "pmk", "Jjzjz", "شسيشس", ".....", plus Khal's own test entries
- **~83% real people, no buying power** (~150): 87% @gmail, 103/181 left NO message; the messages are aspiring-creator wishes ("earn money", "1 mil subs", "become youtuber", "devenir viral comme Mr.Beast", "I want to be famous") — teens/hobbyists worldwide (heavy FR/ES/AR/RU/HI/ID). Only 1 of 181 selected a paid plan.
- **~4% plausible B2B prospects** (~7) — **WORK THESE MANUALLY:**
  - vereine-waggon.5j@icloud.com (Joel — "Lead gen with short-form content", real B2B)
  - meryem_gokmen@alyo.com.tr (corporate Turkish domain, News niche)
  - sidatilambarki2005@gmail.com (Hamza — detailed automation reqs)
  - abidabaidullah9@gmail.com (detailed anime-channel plan — **replied back**)
  - akr.efisa@gmail.com (podcast-to-shorts)
  - hansontagde5@gmail.com (worship band channel)
  - discomanoj@gmail.com

**Correction to earlier "0 replies":** actually ~2% DID reply — `amefresh300420@`, `bab902942@`, `abidabaidullah9@` have `status: replied-back`; `uwe6077@icloud.com` replied before the auto-reply fired. (My first inbox check missed these — they're tracked in leads.json status, not fresh inbox messages.)

## 3. Conclusion + top 2 fixes
**Why ~0 engagement:** deliverability is fine; ~90% of "leads" are broke aspiring creators/teens who wandered into a form for a $997/mo B2B service — no reason or means to convert.
1. **Qualify AT the form** — put the $997/mo price anchor on/near the form + add a required budget or "existing channel URL" field. Kills 90% of junk volume.
2. **Manually work the ~7 real prospects** (personal, non-template) + investigate the traffic source (the FR/AR/HI-heavy Apr 30–May 6 spike = a viral consumer channel, not B2B search) and redirect acquisition toward actual buyers.
