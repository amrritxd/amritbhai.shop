import json, re, html, urllib.request

BASE = "https://amritt-editon-default-rtdb.firebaseio.com/"
FILE = "test.html"
SUBS = ["Maths", "Science", "English", "Hindi"]

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return json.load(r) or {}

def cls_label(c):
    c = str(c); return "Class " + c if c.isdigit() else c

def fmt_time(ms):
    s = round(ms / 1000); return f"{s // 60}m {s % 60:02d}s"

def valid(v):
    try:
        score, total = int(v["score"]), int(v["total"])
    except Exception:
        return None
    name = re.sub(r"\s+", " ", str(v.get("name", ""))).strip()
    if total <= 0 or not (2 <= len(name) <= 40) or not re.fullmatch(r"[^\W\d_]+(?:[ .'-][^\W\d_]+)*\.?", name):
        return None
    try: t = int(v.get("timeMs") or 0)
    except Exception: t = 0
    return {"name": name.title() if name.islower() else name, "cls": cls_label(v.get("cls", "")),
            "score": score, "total": total, "t": t, "at": v.get("createdAt") or 0}

def key(r):  # zyada sahi, phir kam time, phir pehle
    return (-(r["score"] / r["total"]), r["t"] if r["t"] > 0 else 10**12, r["at"])

# All-time topper (testToppers) + fallback: testResults
best = {}
try: tops = get("testToppers.json")
except Exception: tops = {}
for sub in SUBS:
    r = valid(tops.get(sub) or {}) if isinstance(tops.get(sub), dict) else None
    if r: best[sub] = r
for v in get("testResults.json").values():
    if not isinstance(v, dict) or v.get("subject") not in SUBS: continue
    r = valid(v)
    if r and (v["subject"] not in best or key(r) < key(best[v["subject"]])):
        best[v["subject"]] = r
if not best:
    print("Koi valid topper nahi, kuch nahi badla."); raise SystemExit

def line(sub):
    r = best.get(sub)
    if not r: return f"{sub} ka topper abhi tay nahi hua - pehla test dene wale ko mauka hai."
    p = round(r["score"] * 100 / r["total"])
    tm = f" sirf {fmt_time(r['t'])} mein" if r["t"] > 0 else ""
    return f"Amrit Tiwari Test App me {sub} ka all-time topper {r['name']} ({r['cls']}) hai, jisne {r['score']}/{r['total']} ({p}%) score kiya{tm}."

top_sub = min(best, key=lambda s: key(best[s])); r = best[top_sub]
tt = f" in {fmt_time(r['t'])}" if r["t"] > 0 else ""
title = f"Amrit Tiwari Test App Topper: {r['name']} ({r['cls']}) - {r['score']}/{r['total']}{tt} | Amritt Edition"
desc = "Amrit Tiwari Test App ke subject-wise toppers: " + " | ".join(
    f"{s}: {best[s]['name']} ({best[s]['score']}/{best[s]['total']})" if s in best else f"{s}: -" for s in SUBS) + ". Poora leaderboard Amritt Edition par dekhein."
e = lambda s: html.escape(s, quote=True)

faq = [{"@type": "Question", "name": "Amrit Tiwari test app ka topper kaun hai?",
        "acceptedAnswer": {"@type": "Answer", "text": line(top_sub)}}]
for s in SUBS:
    faq.append({"@type": "Question", "name": f"Amrit Tiwari Test App me {s} ka topper kaun hai?",
                "acceptedAnswer": {"@type": "Answer", "text": line(s)}})
ldj = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq}, ensure_ascii=False).replace("<", "\\u003c")

seo = (f'<title>{e(title)}</title><meta name="description" content="{e(desc)}">'
       f'<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
       f'<meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}">'
       f'<script type="application/ld+json">{ldj}</script>')
ns = '<noscript><h1>Amrit Tiwari Test App Topper</h1>' + "".join(
    f"<h2>Amrit Tiwari Test App me {s} ka topper kaun hai?</h2><p>{e(line(s))}</p>" for s in SUBS) + '</noscript>'

s = open(FILE, encoding="utf-8").read()
s2 = re.sub(r"<!--SEO-START-->.*?<!--SEO-END-->", lambda m: "<!--SEO-START-->" + seo + "<!--SEO-END-->", s, flags=re.S)
s2 = re.sub(r"<!--NS-START-->.*?<!--NS-END-->", lambda m: "<!--NS-START-->" + ns + "<!--NS-END-->", s2, flags=re.S)
if s2 != s:
    open(FILE, "w", encoding="utf-8").write(s2); print("Updated:", {k: v["name"] for k, v in best.items()})
else:
    print("Koi badlaav nahi.")
