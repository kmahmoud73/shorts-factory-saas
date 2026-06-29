# Sandy Web Widget — Deploy Guide

The widget (`managed.html`) talks to a backend that holds the Claude key. The site is static (GitHub Pages), so we use a **Cloudflare Worker** (free, stable, no server to keep running). The local `sales_proxy.mjs` + cloudflared quick-tunnel works for *testing* but trial tunnel URLs are temporary — use the Worker for production.

## ✅ Status — LIVE (deployed Jun 28 2026)
- **Worker:** DEPLOYED → `https://sandy-sales.shortsfactory.workers.dev` (account khal.mahmoud@gmail.com, f2a2f373…). Secret `ANTHROPIC_KEY` set. KV `LEADS` bound (id `17a4856eff3546ab9ccb09a7c0588793`).
- **Widget:** wired in `managed.html` (`SALES_API = https://sandy-sales.shortsfactory.workers.dev/chat`) + pushed → LIVE at **shortsfactory.io/managed.html**.
- **Verified end-to-end on production:** bilingual EN/AR sales replies, session memory (KV `sess:*`, 24h TTL), free-sample offer, structured lead capture (KV `lead:*` with name/niche/audience/goal/contact). `/health` → ok.
- **CTAs:** "Book a call" buttons open the live Sandy chat (Calendly not created yet); WhatsApp CTA → dedicated number `wa.me/19144774053` (Hushed 914-477-4053; activate the WhatsApp app to receive).
- **Read leads:** `wrangler kv key list --binding LEADS --remote` then `… key get lead:<ts> --remote`. NOTE: wrangler 4.x `kv` defaults to the LOCAL simulator — always pass `--remote` to see the worker's real data.
- **Pending (Khal, optional):** create the Calendly + repoint CTAs; activate WhatsApp on the Hushed number; wire a push/email alert on new `lead:*`.

## Deploy the Worker (one-time, ~3 min)
```bash
npm install -g wrangler          # if not installed
cd ~/Documents/shorts-factory-saas
wrangler login                   # opens browser — your Cloudflare account
wrangler secret put ANTHROPIC_KEY    # paste the Anthropic key (from api_keys.json)
wrangler deploy                  # -> prints https://sandy-sales.<acct>.workers.dev
```
(Optional, for conversation memory + lead storage: create a KV namespace `wrangler kv namespace create LEADS`, uncomment the `[[kv_namespaces]]` block in `wrangler.toml` with the id, redeploy.)

## Wire the widget
In `managed.html`, find:
```js
var SALES_API = "REPLACE_WITH_BACKEND_URL/chat";
```
Replace with your Worker URL, e.g.:
```js
var SALES_API = "https://sandy-sales.<acct>.workers.dev/chat";
```
Then `git push` (GitHub Pages) → live at **shortsfactory.io/managed.html** with Sandy answering visitors.

## Where leads land
- **Web widget:** the Worker strips the hidden `[[LEAD ...]]` tag; with KV bound, leads are stored as `lead:*` keys (read via `wrangler kv key list`). Wire a webhook/email later if you want push alerts.
- **WhatsApp sales bot** (`wa_assistant/sales.js`): leads → `wa_assistant/logs/leads.jsonl`.

## Test locally (no deploy)
```bash
node sales_proxy.mjs                       # proxy on 127.0.0.1:8027
curl -s -XPOST localhost:8027/chat -H 'content-type: application/json' -d '{"message":"I want an Arabic cooking channel"}'
```
