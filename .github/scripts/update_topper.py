import json, re, html, urllib.request

DB = "https://amritt-editon-default-rtdb.firebaseio.com/testResults.json"
FILE = "test.html"

def cls_label(c):
    c = str(c)
    return "Class " + c if c.isdigit() else c

def praise(p):
    if p >= 90: return "Shandar pradarshan, bahut hi talented aur mehnati student!"
    if p >= 75: return "Bahut badhiya performance, kabil-e-tareef mehnat!"
    if p >= 50: return "Achha prayas, mehnat rang laa rahi hai!"
    return "Sabse aage rehne ke liye badhai, aur mehnat karte rahein!"

with urllib.request.urlopen(DB, timeout=30) as r:
    data = json.load(r) or {}

rows = []
for k, v in data.items():
    if not isinstance(v, dict): continue
    try:
        score, total = int(v["score"]), int(v["total"])
    except Exception:
        continue
    name = re.sub(r"\s+", " ", str(v.get("name", ""))).strip()
    if total <= 0 or not (2 <= len(name) <= 40) or not re.fullmatch(r"[^\W\d_]+(?:[ .'-][^\W\d_]+)*\.?", name):
        continue
    rows.append((-(score / total), -score, v.get("createdAt") or 0, name, v))
if not rows:
    print("Koi valid result nahi, kuch nahi badla."); raise SystemExit

rows.sort(key=lambda x: x[:3])
v = rows[0][4]; name = rows[0][3]
score, total = int(v["score"]), int(v["total"]); pct = round(score * 100 / total)
cls = cls_label(v.get("cls", "")); sub = str(v.get("subject") or "test")[:40]
name_t = name.title() if name.islower() else name

title = f"Amrit Tiwari Test App Topper: {name_t} ({cls}) - {score}/{total} | Amritt Edition"
desc = (f"Amrit Tiwari Test App ka topper kaun hai? {name_t} ({cls}) ne {sub} mein {score}/{total} ({pct}%) "
        f"score karke leaderboard mein pehla sthan paya. {praise(pct)} Poora leaderboard Amritt Edition par dekhein.")
answer = f"Amrit Tiwari Test App ke leaderboard ka topper {name_t} ({cls}) hai, jisne {sub} mein {score}/{total} ({pct}%) score kiya. {praise(pct)}"
e = lambda s: html.escape(s, quote=True)

ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{
    "@type": "Question", "name": "Amrit Tiwari test app ka topper kaun hai?",
    "acceptedAnswer": {"@type": "Answer", "text": answer}}]}
ldj = json.dumps(ld, ensure_ascii=False).replace("<", "\\u003c")

seo = (f'<title>{e(title)}</title>'
       f'<meta name="description" content="{e(desc)}">'
       f'<meta property="og:title" content="{e(title)}">'
       f'<meta property="og:description" content="{e(desc)}">'
       f'<meta name="twitter:title" content="{e(title)}">'
       f'<meta name="twitter:description" content="{e(desc)}">'
       f'<script type="application/ld+json">{ldj}</script>')
ns = f'<noscript><h1>Amrit Tiwari Test App Topper</h1><p>{e(answer)}</p></noscript>'

s = open(FILE, encoding="utf-8").read()
s2 = re.sub(r"<!--SEO-START-->.*?<!--SEO-END-->", lambda m: "<!--SEO-START-->" + seo + "<!--SEO-END-->", s, flags=re.S)
s2 = re.sub(r"<!--NS-START-->.*?<!--NS-END-->", lambda m: "<!--NS-START-->" + ns + "<!--NS-END-->", s2, flags=re.S)
if s2 != s:
    open(FILE, "w", encoding="utf-8").write(s2); print("Updated topper:", name_t, cls, score, total)
else:
    print("Koi badlaav nahi.")
