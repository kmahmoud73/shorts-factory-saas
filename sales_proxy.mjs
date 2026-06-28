// Sales chat proxy — holds the Claude key server-side so the website widget can
// chat with Sandy (Haiku) safely. CORS-open for the static site. Logs leads.
// Run on the Mac; expose via a cloudflared tunnel. (Production: move to a CF Worker.)
import http from 'node:http';
import fs from 'node:fs';

const KEY = (() => {
  const a = JSON.parse(fs.readFileSync('/Users/digisov/Documents/shorts-factory/api_keys.json', 'utf8')).anthropic;
  return typeof a === 'string' ? a : (a.api_key || a.key || a.token);
})();
const SYS = fs.readFileSync(process.env.HOME + '/.sandy_sales/SALES.md', 'utf8');
const MODEL = 'claude-haiku-4-5-20251001';
const LEADS = '/Users/digisov/Documents/shorts-factory-saas/web_leads.jsonl';
const PORT = 8027;
const sessions = {}; // sid -> messages

http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'content-type');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method === 'GET' && req.url === '/health') { res.writeHead(200); res.end('ok'); return; }
  if (req.method === 'POST' && req.url === '/chat') {
    let body = '';
    req.on('data', (c) => { body += c; if (body.length > 1e5) req.destroy(); });
    req.on('end', async () => {
      try {
        const { message, session } = JSON.parse(body || '{}');
        if (!message) { res.writeHead(400); res.end('{}'); return; }
        const sid = session || Math.random().toString(36).slice(2);
        const conv = sessions[sid] || [];
        conv.push({ role: 'user', content: String(message).slice(0, 2000) });
        const r = await fetch('https://api.anthropic.com/v1/messages', {
          method: 'POST',
          headers: { 'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
          body: JSON.stringify({ model: MODEL, max_tokens: 500, system: SYS, messages: conv.slice(-16) }),
        });
        const j = await r.json();
        let reply = (j.content && j.content[0] && j.content[0].text || '').trim()
          || "Hi! I'm Sandy 👋 tell me the niche you'd want a faceless channel in and I'll send you a free sample clip.";
        conv.push({ role: 'assistant', content: reply });
        sessions[sid] = conv;
        const m = reply.match(/\[\[LEAD[^\]]*\]\]/);
        if (m) { try { fs.appendFileSync(LEADS, JSON.stringify({ ts: Date.now(), sid, tag: m[0] }) + '\n'); } catch {} reply = reply.replace(m[0], '').trim(); }
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ reply, session: sid }));
      } catch (e) { res.writeHead(500); res.end(JSON.stringify({ error: e.message })); }
    });
    return;
  }
  res.writeHead(404); res.end();
}).listen(PORT, '127.0.0.1', () => console.log('sales proxy on 127.0.0.1:' + PORT));
process.on('uncaughtException', (e) => console.error('uncaught: ' + e.message));
