# Sandy Web Widget — Deploy Guide

The widget (`managed.html`) talks to a backend that holds the Claude key. The site is static (GitHub Pages), so we use a **Cloudflare Worker** (free, stable, no server to keep running). The local `sales_proxy.mjs` + cloudflared quick-tunnel works for *testing* but trial tunnel URLs are temporary — use the Worker for production.

## ✅ Status
- **Widget UI:** built + injected into `managed.html` (floating bubble, bottom-right).
- **Sandy sales brain:** WORKS — verified end-to-end on localhost (perfect bilingual sales replies, offers the free sample, captures `[[LEAD]]`).
- **Backend code:** `worker.js` (Cloudflare Worker) ready. `sales_proxy.mjs` = local test version.
- **Pending:** deploy the Worker (needs your Cloudflare login, ~3 min) + paste its URL into the widget.

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
