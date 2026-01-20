import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# PAGE CONFIG
st.set_page_config(
    page_title="Global Telco/OTT/Sports/Tech Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# AUTO-REFRESH + KEEP-ALIVE
@st.fragment(run_every=300)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

st.markdown('<script>setTimeout(function(){window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

# STYLING (enhanced for readability)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; font-family: 'Inter', sans-serif; padding-top: 0.5rem; }
    .header-container { background: rgba(255,255,255,0.96); padding: 1.5rem 2rem; text-align: center; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.15); margin: 0 0 2rem 0; border-bottom: 4px solid #1e40af; }
    .main-title { font-size: 2.6rem; font-weight: 800; color: #0a192f; margin: 0; letter-spacing: -0.8px; }
    .subtitle { font-size: 1.1rem; color: #475569; margin-top: 0.6rem; font-weight: 500; }
    .hero-container { background: rgba(255,255,255,0.98); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 10px 35px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; }
    .hero-title { color: #0a192f; font-size: 1.85rem; font-weight: 800; margin-bottom: 1.5rem; border-left: 6px solid #1e40af; padding-left: 15px; }
    .col-header { padding: 12px 16px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; font-size: 0.95rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .col-body { background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 480px; max-height: 580px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    .news-card, .news-card-priority { background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px; transition: all 0.3s ease; }
    .news-card-priority { background: linear-gradient(135deg, #fff5f5, #fef2f2); border: 2px solid #fca5a5; box-shadow: 0 4px 12px rgba(239,68,68,0.15); position: relative; }
    .news-card-priority::before { content: "⚡ PRIORITY"; position: absolute; top: -8px; right: 10px; background: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
    .news-card:hover, .news-card-priority:hover { box-shadow: 0 6px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }
    .news-title { color: #1e40af; font-size: 0.92rem; font-weight: 600; line-height: 1.35; text-decoration: none; display: block; margin-bottom: 6px; }
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    .news-meta { font-size: 0.76rem; color: #64748b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
    .impact-badge { background: #dc2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
    .time-hot {color: #dc2626; font-weight: 600; font-style: italic;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# KEYWORDS (global focus, boosted for strategic + recent Evergent/NBA signal)
TELCO_KEYWORDS = {
    "must_have": ["oss", "bss", "billing", "charging", "5g", "6g", "network", "telecom", "carrier", "operator"],
    "strategic": ["merger", "acquisition", "partnership", "deal", "contract", "deploy", "modernization", "monetization"],
    "companies": ["ericsson", "nokia", "huawei", "amdocs", "netcracker", "csg", "oracle communications", "matrixx", "optiva", "cerillion", "mavenir"]
}
OTT_KEYWORDS = {
    "must_have": ["ott", "streaming", "subscription", "svod", "avod", "content platform"],
    "strategic": ["content deal", "licensing", "rights", "subscriber", "launch platform", "merger"],
    "companies": ["netflix", "disney", "paramount", "peacock", "prime video", "max", "shahid", "viki", "sky", "astro", "bbc iplayer", "directv"]
}
SPORTS_KEYWORDS = {
    "must_have": ["sports", "media rights", "broadcasting", "streaming rights", "league"],
    "strategic": ["rights deal", "broadcast contract", "partnership", "investment"],
    "companies": ["nba", "nfl", "premier league", "espn", "fox sports", "dazn", "bally sports", "sportspromedia"]
}
TECH_KEYWORDS = {
    "must_have": ["ai", "artificial intelligence", "startup", "funding", "tech"],
    "strategic": ["raises", "funding round", "acquires", "merger", "investment", "valuation", "ipo"],
    "companies": ["openai", "anthropic", "google", "microsoft", "meta", "nvidia", "amazon"]
}

NOISE_BLOCKLIST = [
    "opinion", "op-ed", "analysis", "how to", "guide", "tips", "best practices", "podcast", "webinar", "awards", "anniversary", "prediction", "betting"
]

# PRIORITY LISTS (flattened from your dicts, global focus, added "evergent")
EVERGENT_CLIENTS_KWS = ["nba", "astro", "shahid", "fox sports", "directv", "tv asahi", "abs-cbn", "viki", "trt", "sonyliv", "bbc iplayer", "sky", "telekom malaysia", "cignal", "aha", "britbox", "lightbox", "evergent"]
COMPETITORS_KWS = ["netcracker", "amdocs", "csg", "oracle communications", "ericsson", "nokia", "huawei", "matrixx", "optiva", "cerillion", "mavenir"]
TOP_TELCOS_KWS = ["verizon", "at&t", "t-mobile", "vodafone", "deutsche telekom", "orange", "telefonica", "bt group", "singtel", "telstra", "ntt docomo", "china mobile"]
ALL_PRIORITY_KWS = set(k.lower() for k in EVERGENT_CLIENTS_KWS + COMPETITORS_KWS + TOP_TELCOS_KWS)

ALL_COMPANY_KWS = list(ALL_PRIORITY_KWS)

# RSS FEEDS - GLOBAL, UPDATED 2026 (high-signal for deals, funding, rights)
RSS_FEEDS = [
    # TELCO OSS/BSS global
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Total Telecom", "https://totaltele.com/feed/", "telco"),

    # OTT Streaming global
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("Streaming Media", "https://feeds.feedburner.com/StreamingMediaMagazine-AllArticles", "ott"),
    ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
    ("Fierce Video", "https://www.fiercevideo.com/rss.xml", "ott"),

    # SPORTS Media Rights / Broadcasting
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("Sportcal", "https://www.sportcal.com/feed", "sports"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),

    # TECH AI / M&A / Funding
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("WIRED", "https://www.wired.com/feed/rss", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA RIGHTS", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "TECH AI / M&A", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def is_noise(text):
    text_lower = text.lower()
    return any(n in text_lower for n in NOISE_BLOCKLIST)

def calculate_relevance(title, summary, category):
    text = (title + " " + summary).lower()
    score = 0

    keywords = {
        "telco": TELCO_KEYWORDS, "ott": OTT_KEYWORDS,
        "sports": SPORTS_KEYWORDS, "technology": TECH_KEYWORDS
    }[category]

    if any(kw in text for kw in keywords["must_have"]):
        score += 20
    if any(kw in text for kw in keywords["strategic"]):
        score += 35  # Boost for deals/funding/rights
    if any(c in text for c in keywords["companies"]):
        score += 25
    if any(c in text for c in ALL_PRIORITY_KWS):
        score += 30  # High boost for clients/competitors/top telcos
        if "evergent" in text or "nba" in text:  # Recent Jan 2026 NBA investment signal
            score += 40

    # Global/strategic bonus
    if any(w in text for w in ["global", "international", "deal", "investment", "rights", "acquisition", "merger"]):
        score += 15

    return score

def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        sig = re.sub(r'[^\w\s]', '', item['title'].lower())
        sig = ' '.join(sorted(sig.split()[:10]))
        if sig not in seen:
            seen.add(sig)
            unique.append(item)
    return unique

def fetch_feed(source, url, cat):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now(timezone.utc)
        CUTOFF = NOW - timedelta(days=3)
        for entry in feed.entries[:80]:
            title = clean(entry.title or "")
            summary = clean(entry.get("summary") or entry.get("description") or title)
            if len(title) < 25 or is_noise(title + summary):
                continue
            link = entry.link or ""
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    pub = datetime(*val[:6], tzinfo=timezone.utc)
                    break
            if not pub or pub < CUTOFF:
                continue
            rel = calculate_relevance(title, summary, cat)
            if rel < 12:
                continue
            full = (title + " " + summary).lower()
            prio = any(c in full for c in ALL_PRIORITY_KWS)
            items.append({
                "title": title, "link": link, "pub": pub, "source": source,
                "summary": summary[:120] + "..." if len(summary) > 120 else summary,
                "category": cat, "priority": prio, "score": rel
            })
    except Exception:
        pass
    return items

@st.cache_data(ttl=180)
def load_data():
    cats = {"telco": [], "ott": [], "sports": [], "technology": []}
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for fut in as_completed(futures):
            for it in fut.result():
                cats[it["category"]].append(it)
    for c in cats:
        cats[c] = deduplicate(cats[c])
        cats[c].sort(key=lambda x: (-x["pub"].timestamp(), -x["score"]))  # recency first
    return cats

def time_str(dt):
    hrs = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if hrs < 1: return "Now"
    if hrs < 6: return f"{hrs}h ago"
    return f"{hrs}h ago" if hrs < 24 else f"{hrs//24}d ago"

def time_class(dt):
    hrs = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if hrs < 6: return "time-hot"
    if hrs < 24: return "time-warm"
    return "time-normal"

def render_items(items):
    if not items: return '<div style="text-align:center;padding:40px;color:#94a3b8;">Scanning global signals...</div>'
    cards = []
    for it in items[:10]:
        tcls = time_class(it["pub"])
        tstr = time_str(it["pub"])
        cls = "news-card-priority" if it["priority"] else "news-card"
        badge = '<span class="impact-badge">CRITICAL</span>' if it["score"] >= 70 else ""
        html_card = f'''
        <div class="{cls}">
            <a href="{html.escape(it["link"])}" target="_blank" class="news-title">{html.escape(it["title"])}</a>
            <div class="news-meta">
                <span class="{tcls}">{tstr}</span> • <span>{html.escape(it["source"])}</span> {badge}
            </div>
        </div>'''
        cards.append(html_card)
    return '<div class="col-body">' + ''.join(cards) + '</div>'

# STRATEGIC DASHBOARD
@st.cache_data(ttl=600)
def top_signals(data):
    all_it = [i for sub in data.values() for i in sub]
    all_it.sort(key=lambda x: -x["score"])
    return [{"title": i["title"], "source": i["source"]} for i in all_it[:3]]

@st.cache_data(ttl=600)
def market_pulse(data):
    all_it = [i for sub in data.values() for i in sub]
    mentions = {}
    for i in all_it:
        txt = (i["title"] + " " + i["summary"]).lower()
        for c in ALL_PRIORITY_KWS:
            if c in txt:
                mentions[c] = mentions.get(c, 0) + 1
    top = sorted(mentions.items(), key=lambda x: -x[1])[:4]
    return [f"<b>{c.upper()}:</b> {cnt} mentions" for c, cnt in top]

# UI
placeholder = st.empty()
with placeholder.container():
    st.markdown('<div style="text-align:center;height:70vh;display:flex;flex-direction:column;justify-content:center;"><h1 style="color:#0a192f;font-size:2.8rem;">⚡ Global Intelligence Engine</h1><p>Scanning Telco • OTT • Sports • AI/Tech</p></div>', unsafe_allow_html=True)
    time.sleep(1.2)
placeholder.empty()

st.markdown('<div class="header-container"><h1 class="main-title">Global Telco/OTT/Sports/Tech Nexus</h1><p class="subtitle">Executive Signals • M&A • Rights • Funding • Partnerships</p></div>', unsafe_allow_html=True)

with st.spinner("🔍 Scanning latest global signals..."):
    data = load_data()
    hits = top_signals(data)
    pulse = market_pulse(data)

hits_html = "".join(f"<b>#{i+1}:</b> {h['title']}<br><small>({h['source']})</small><br><br>" for i, h in enumerate(hits)) or "<i>Monitoring high-impact moves...</i>"
pulse_html = "".join(p + "<br><br>" for p in pulse) or "<i>Trends loading...</i>"

tot = sum(len(v) for v in data.values())
prio = sum(1 for v in data.values() for i in v if i['priority'])
crit = sum(1 for v in data.values() for i in v if i['score'] >= 70)

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🎯 Executive Intelligence Overview</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div class="hero-box"><div class="hero-box-title" style="color:#dc2626;">🔥 TOP STRATEGIC SIGNALS</div><div class="hero-content">{hits_html}</div></div>
        <div class="hero-box"><div class="hero-box-title" style="color:#10b981;">📈 MARKET PULSE</div><div class="hero-content">{pulse_html}<div style="margin-top:15px;border-top:1px solid #e2e8f0;padding-top:15px;"><b>Total:</b> {tot} | <b>Priority:</b> {prio} | <b>Critical:</b> {crit}</div></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    with cols[idx]:
        sec = SECTIONS[cat]
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_items(data.get(cat, [])), unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center;color:#fff;font-size:0.8rem;margin:20px;padding:16px;background:linear-gradient(135deg,#0a192f,#1e293b);border-radius:10px;">
    <strong>Focus:</strong> Global M&A • Rights • Investments • Launches | <strong>Last Update:</strong> {datetime.now().strftime('%I:%M %p %Z')} | <strong>Refresh:</strong> every 5 min
</div>
""", unsafe_allow_html=True)

keep_alive()
