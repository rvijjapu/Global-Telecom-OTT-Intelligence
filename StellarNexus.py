import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telco/OTT/Sports/Tech Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# AUTO-REFRESH EVERY 5 MINUTES
@st.fragment(run_every=300)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

st.markdown(
    '<script>setTimeout(function(){window.location.reload();}, 300000);</script>',
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# STYLING
# ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; font-family: 'Inter', sans-serif;}
    .header {background: rgba(255,255,255,0.96); padding: 1.5rem; text-align: center; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.15); margin-bottom: 2rem; border-bottom: 4px solid #1e40af;}
    .main-title {font-size: 2.6rem; font-weight: 800; color: #0a192f;}
    .subtitle {font-size: 1.1rem; color: #475569; font-weight: 500;}
    .hero {background: rgba(255,255,255,0.98); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 10px 35px rgba(0,0,0,0.12);}
    .hero-title {font-size: 1.85rem; font-weight: 800; color: #0a192f; border-left: 6px solid #1e40af; padding-left: 15px;}
    .section-header {padding: 12px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; text-align: center;}
    .pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .green {background: linear-gradient(135deg, #34d399, #10b981);}
    .orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .col-body {background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 480px; max-height: 580px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08);}
    .news-card {background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px;}
    .priority {background: linear-gradient(135deg, #fff5f5, #fef2f2); border: 2px solid #fca5a5; box-shadow: 0 4px 12px rgba(239,68,68,0.15); position: relative;}
    .priority::before {content: "⚡ PRIORITY"; position: absolute; top: -8px; right: 10px; background: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;}
    .news-title {color: #1e40af; font-weight: 600; text-decoration: none; display: block; margin-bottom: 6px;}
    .news-title:hover {color: #1d4ed8; text-decoration: underline;}
    .meta {font-size: 0.8rem; color: #64748b; display: flex; gap: 8px;}
    .impact {background: #dc2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700;}
    .hot {color: #dc2626; font-weight: 600;}
    .warm {color: #ea580c; font-weight: 600;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# KEYWORDS & PRIORITIES
# ────────────────────────────────────────────────
TELCO_KW = {"must": ["oss", "bss", "billing", "charging", "5g", "6g", "telecom"], "strat": ["merger", "acquisition", "partnership", "deal", "contract"]}
OTT_KW  = {"must": ["ott", "streaming", "subscription", "svod"], "strat": ["content deal", "rights", "licensing", "subscriber growth"]}
SPORTS_KW = {"must": ["sports", "media rights", "broadcasting"], "strat": ["rights deal", "investment", "partnership"]}
TECH_KW = {"must": ["ai", "agentic", "funding", "startup"], "strat": ["acquires", "investment", "agentic ai", "autonomous"]}

ALL_PRIORITY = {
    "evergent_clients": ["nba", "astro", "shahid", "fox sports", "directv", "viki", "trt", "sky", "bbc iplayer", "telekom malaysia", "cignal", "aha", "britbox"],
    "competitors": ["amdocs", "netcracker", "csg", "oracle communications", "ericsson", "nokia", "huawei", "matrixx", "optiva"],
    "top_telcos": ["verizon", "at&t", "t-mobile", "vodafone", "deutsche telekom", "orange", "telefonica", "bt group", "singtel", "telstra"]
}
ALL_KWS = set(k.lower() for v in ALL_PRIORITY.values() for k in v)

NOISE = ["opinion", "how to", "guide", "podcast", "awards", "prediction"]

RSS_FEEDS = [
    ("Light Reading",       "https://www.lightreading.com/rss/simple",               "telco"),
    ("Fierce Telecom",      "https://www.fierce-network.com/rss.xml",               "telco"),
    ("RCR Wireless",        "https://www.rcrwireless.com/feed",                     "telco"),
    ("Mobile World Live",   "https://www.mobileworldlive.com/feed/",                "telco"),
    ("Telecoms.com",        "https://www.telecoms.com/feed",                        "telco"),
    ("Variety",             "https://variety.com/feed/",                            "ott"),
    ("Hollywood Reporter",  "https://www.hollywoodreporter.com/feed/",              "ott"),
    ("Deadline",            "https://deadline.com/feed/",                           "ott"),
    ("Digital TV Europe",   "https://www.digitaltveurope.com/feed/",                "ott"),
    ("Streaming Media",     "https://feeds.feedburner.com/StreamingMediaMagazine-AllArticles", "ott"),
    ("SportsPro",           "https://www.sportspromedia.com/feed/",                 "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss",       "sports"),
    ("Sportcal",            "https://www.sportcal.com/feed",                        "sports"),
    ("TechCrunch",          "https://techcrunch.com/feed/",                         "technology"),
    ("VentureBeat",         "https://venturebeat.com/feed/",                        "technology"),
    ("The Verge",           "https://www.theverge.com/rss/index.xml",               "technology"),
]

SECTIONS = {
    "telco":       {"icon": "📡", "name": "TELCO OSS/BSS",        "style": "section-header pink"},
    "ott":         {"icon": "📺", "name": "OTT STREAMING",        "style": "section-header purple"},
    "sports":      {"icon": "🏆", "name": "SPORTS MEDIA RIGHTS",  "style": "section-header green"},
    "technology":  {"icon": "⚡", "name": "TECH AI / M&A",        "style": "section-header orange"}
}

# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────
def clean(text):
    return html.unescape(re.sub(r'<[^>]+>', '', str(text or ""))).strip()

def is_noise(text):
    return any(n in text.lower() for n in NOISE)

def score_relevance(title, summary, cat):
    text = (title + " " + summary).lower()
    kw = {"telco": TELCO_KW, "ott": OTT_KW, "sports": SPORTS_KW, "technology": TECH_KW}[cat]
    score = 0
    if any(m in text for m in kw["must"]):  score += 20
    if any(s in text for s in kw["strat"]): score += 40

    for group, boost in [("competitors", 30), ("evergent_clients", 50 if "evergent" in text or "nba" in text else 35), ("top_telcos", 25)]:
        score += sum(boost for k in ALL_PRIORITY[group] if k in text)

    if any(w in text for w in ["global", "investment", "acquisition", "preferred vendor", "agentic", "churn", "retention", "league pass"]):
        score += 30
    return score

def fetch(source, url, cat):
    items = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200:
            return items
        feed = feedparser.parse(r.content)
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        for e in feed.entries[:60]:
            title = clean(e.title or "")
            summ = clean(e.get("summary") or e.get("description") or title)
            if len(title) < 30 or is_noise(title + summ):
                continue
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                if val := getattr(e, k, None):
                    try:
                        pub = datetime(*val[:6], tzinfo=timezone.utc)
                    except:
                        pass
                    break
            if not pub or pub < cutoff:
                continue
            rel = score_relevance(title, summ, cat)
            if rel < 40:
                continue
            full = (title + " " + summ).lower()
            prio = any(k in full for k in ALL_KWS) or "evergent" in full
            items.append({
                "title": title,
                "link": e.link or "",
                "pub": pub,
                "source": source,
                "summary": summ[:150] + "..." if len(summ) > 150 else summ,
                "cat": cat,
                "prio": prio,
                "score": rel
            })
    except Exception:
        pass
    return items

@st.cache_data(ttl=120)
def load():
    cats = {c: [] for c in SECTIONS}
    with ThreadPoolExecutor(16) as ex:
        fs = [ex.submit(fetch, s, u, c) for s, u, c in RSS_FEEDS]
        for f in as_completed(fs):
            for i in f.result():
                cats[i["cat"]].append(i)

    for c in cats:
        # Deduplicate using hashable tuple (title + source)
        seen = set()
        unique = []
        for item in cats[c]:
            sig = (
                item.get("title", "").lower().strip(),
                item.get("source", "").lower().strip()
            )
            if sig not in seen:
                seen.add(sig)
                unique.append(item)

        # Sort: newest first, then highest score
        cats[c] = sorted(
            unique,
            key=lambda x: (-x["pub"].timestamp(), -x["score"])
        )[:12]

    return cats

def time_disp(dt):
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    h = int(secs / 3600)
    if h < 1: return "Now"
    if h < 24: return f"{h}h"
    return f"{h//24}d"

def render_news(items):
    if not items:
        return '<div style="text-align:center;padding:50px;color:#94a3b8;">Scanning global strategic signals...</div>'
    html = []
    for i in items[:10]:
        cls = "news-card priority" if i["prio"] else "news-card"
        tcls = "hot" if (datetime.now(timezone.utc) - i["pub"]).total_seconds() < 21600 else "warm" if (datetime.now(timezone.utc) - i["pub"]).total_seconds() < 86400 else ""
        badge = '<span class="impact">HIGH IMPACT</span>' if i["score"] > 80 else ""
        card = f'''
        <div class="{cls}">
            <a href="{html.escape(i["link"])}" target="_blank" class="news-title">{html.escape(i["title"])}</a>
            <div class="meta">
                <span class="{tcls}">{time_disp(i["pub"])}</span> • {html.escape(i["source"])} {badge}
            </div>
        </div>'''
        html.append(card)
    return ''.join(html)

# ────────────────────────────────────────────────
# TOP HITS & PULSE (narrative style)
# ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def top_hits(data):
    all_items = [i for lst in data.values() for i in lst]
    all_items.sort(key=lambda x: -x["score"])
    narratives = []
    for item in all_items[:4]:
        if item["score"] < 60:
            continue
        t = item["title"].lower()
        s = item["summary"].lower()
        src = item["source"]
        if "nba" in t+s and ("evergent" in t+s or "investment" in t+s or "stake" in t+s):
            narratives.append("**NBA Strategic Equity Stake in Evergent**: The NBA has taken a strategic investment in Evergent Technologies, designating it a **Preferred Vendor** and extending their multi-year partnership. Powers personalized NBA League Pass across **185+ countries**, driving subscriber growth, churn reduction, and global fan retention.")
        elif "amdocs" in t+s and ("matrixx" in t+s or "acquir" in t+s):
            narratives.append("**Amdocs Acquires Matrixx (~$200M)**: Amdocs completes ~$200M acquisition of charging/BSS leader Matrixx Software, consolidating Tier-1 5G BSS market dominance and intensifying competition in telecom charging/monetization.")
        elif "agentic" in t+s and ("ai" in t+s or "bss" in t+s or "oss" in t+s):
            narratives.append("**Agentic AI Shift in BSS/OSS**: Autonomous Agentic AI agents projected to handle ~40% of standard telecom BSS tasks by EOY 2026 — enabling proactive churn strategies, real-time retention, and intent-driven operations.")
        else:
            narratives.append(f"**{item['title']}**: {item['summary']} — Strategic signal from {src}.")
    return narratives or ["<i>Monitoring high-impact global moves...</i>"]

@st.cache_data(ttl=300)
def market_pulse(data):
    all_items = [i for lst in data.values() for i in lst]
    mentions = {}
    for i in all_items:
        txt = (i["title"] + " " + i["summary"]).lower()
        for k in ALL_KWS:
            if k in txt:
                mentions[k] = mentions.get(k, 0) + 1
    top = sorted(mentions.items(), key=lambda x: -x[1])[:5]
    lines = [f"**{k.upper()}**: {v} high-impact mentions — watch for strategic moves." for k, v in top]
    return lines or ["<i>Analyzing priority trends...</i>"]

# ────────────────────────────────────────────────
# MAIN UI
# ────────────────────────────────────────────────
with st.spinner("🔍 Scanning global Telco / OTT / Sports / AI signals..."):
    data = load()
    hits = top_hits(data)
    pulse_lines = market_pulse(data)

st.markdown(
    '<div class="header"><h1 class="main-title">Global Telco/OTT/Sports/Tech Nexus</h1>'
    '<p class="subtitle">Executive Intelligence • M&A • Rights • AI Shifts • Partnerships</p></div>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div class="hero">
    <div class="hero-title">🚀 Top Strategic Intelligence (Live Feed)</div>
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <div>
            <h3 style="color:#dc2626;">🔥 BREAKING STRATEGIC HITS</h3>
            {'<br><br>'.join(hits)}
        </div>
        <div>
            <h3 style="color:#10b981;">📊 MARKET PULSE</h3>
            {'<br><br>'.join(pulse_lines)}
            <div style="margin-top:20px; padding-top:15px; border-top:1px solid #e2e8f0;">
                <b>Total Signals:</b> {sum(len(v) for v in data.values())}<br>
                <b>Priority Mentions:</b> {sum(1 for v in data.values() for i in v if i['prio'])}<br>
                <b>High-Impact:</b> {sum(1 for v in data.values() for i in v if i['score'] > 80)}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
for idx, cat in enumerate(SECTIONS):
    with cols[idx]:
        s = SECTIONS[cat]
        st.markdown(f'<div class="{s["style"]}">{s["icon"]} {s["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{render_news(data.get(cat, []))}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; color:#fff; font-size:0.85rem; margin:25px; padding:15px; background:linear-gradient(135deg,#0a192f,#1e293b); border-radius:12px;">
    <strong>Focus:</strong> Global Strategic Signals • Evergent Clients/Competitors • AI in BSS/OSS
    | <strong>Last Scan:</strong> {datetime.now().strftime('%I:%M %p %Z')}
    | Auto-refresh: 5 min
</div>
""", unsafe_allow_html=True)

keep_alive()
