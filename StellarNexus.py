import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus – AI Powered Real-time Competitive Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Health check endpoint
if st.query_params.get("ping") == "1":
    st.write("alive")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT FILTER
# ─────────────────────────────────────────────────────────────────────────────
BLACKLIST_WORDS = [
    "sexual", "porn", "xxx", "adult", "explicit", "nude", "nsfw",
    "murder", "killing", "shooter", "terrorist", "massacre", "rape", "assault",
    "scandal", "affair", "divorce", "lawsuit", "fraud", "corruption",
    "celebrity breakup", "dating rumors", "feud", "controversy",
    "casino", "gambling", "tobacco", "drug", "overdose",
    "ponzi", "scam", "pyramid scheme", "crypto crash", "gossip", "rumor",
    "score", "injury", "fantasy", "betting"
]

def is_content_appropriate(title, summary=""):
    content = f"{title} {summary}".lower()
    return not any(word in content for word in BLACKLIST_WORDS)

# ─────────────────────────────────────────────────────────────────────────────
# EVERGENT DATA LAYERS
# ─────────────────────────────────────────────────────────────────────────────
EVERGENT_CLIENTS = { … }       # ← paste your full EVERGENT_CLIENTS dict here

COMPETITORS = { … }            # ← paste your full COMPETITORS dict here

TOP_TELCOS = { … }             # ← paste your full flat TOP_TELCOS dict here

# Scoring signals (your original – can be tuned later)
TELCO_SIGNALS = { … }
OTT_SIGNALS  = { … }
SPORTS_SIGNALS = { … }
AI_SIGNALS   = { … }

def calculate_relevance_score(title, summary, category):
    content = f"{title} {summary}".lower()
    score = 0

    signals = {
        "telco": TELCO_SIGNALS,
        "ott": OTT_SIGNALS,
        "sports": SPORTS_SIGNALS,
        "technology": AI_SIGNALS
    }.get(category, {})

    if not signals:
        return 0

    if any(neg in content for neg in signals.get("negative", [])):
        return 0

    score += sum(50 for kw in signals.get("tier1", []) if kw in content)
    score += sum(25 for kw in signals.get("tier2", []) if kw in content)
    score += sum(10 for kw in signals.get("tier3", []) if kw in content)

    # Hidden boosts – priority for Evergent ecosystem
    if any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values()):
        score += 80

    if any(any(v in content for v in vs) for vs in COMPETITORS.values()):
        score += 60

    if any(any(v in content for v in vs) for vs in TOP_TELCOS.values()):
        score += 30

    action_kws = [
        "acquisition", "merger", "partnership", "deal", "extension", "investment",
        "strategic", "wins", "award", "deploy", "scale", "growth", "churn reduction",
        "monetization", "subscriber growth", "arpu", "billing transformation",
        "oss transformation", "5g monetization", "real-time charging", "revenue",
        "content deal", "media rights"
    ]
    score += sum(25 for kw in action_kws if kw in content)

    # Recent big news boost
    if "nba" in content and any(kw in content for kw in ["investment", "strategic", "extension", "partnership"]):
        score += 90

    return min(score, 100)

def classify_article(title, summary, category):
    content = f"{title} {summary}".lower()
    score = calculate_relevance_score(title, summary, category)

    if score < 55:
        return "IRRELEVANT", "", 999

    is_client      = any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values())
    is_competitor  = any(any(v in content for v in vs) for vs in COMPETITORS.values())

    if is_client or is_competitor:
        badge = "🌟" if is_client else "⚠️"
        prio  = 0 if is_client else 1
        return "HIGH", badge, prio

    badges = {
        "telco":      ("TELCO", "📡", 5),
        "ott":        ("OTT",   "📺", 6),
        "sports":     ("SPORTS","🏆", 7),
        "technology": ("TECH",  "⚡", 8)
    }
    b, icon, prio = badges.get(category, ("", "", 999))
    return "NORMAL", icon, prio

# ─────────────────────────────────────────────────────────────────────────────
# RSS SOURCES – clean & focused
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com",       "https://www.telecoms.com/feed",                    "telco"),
    ("Light Reading",      "https://www.lightreading.com/rss/simple",          "telco"),
    ("Fierce Telecom",     "https://www.fierce-network.com/rss.xml",           "telco"),
    ("RCR Wireless",       "https://www.rcrwireless.com/feed",                 "telco"),
    ("Mobile World Live",  "https://www.mobileworldlive.com/feed/",            "telco"),
    ("TelecomTV",          "https://www.telecomtv.com/feed",                   "telco"),
    ("TM Forum",           "https://inform.tmforum.org/feed/",                 "telco"),
    ("Variety",            "https://variety.com/feed/",                        "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/",          "ott"),
    ("Deadline",           "https://deadline.com/feed/",                       "ott"),
    ("Streaming Media",    "https://www.streamingmedia.com/rss",               "ott"),
    ("Cord Cutters News",  "https://www.cordcuttersnews.com/feed/",            "ott"),
    ("ESPN",               "https://www.espn.com/espn/rss/news",               "sports"),
    ("SportsPro",          "https://www.sportspromedia.com/feed/",             "sports"),
    ("SportBusiness",      "https://www.sportbusiness.com/feed/",              "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss",   "sports"),
    ("TV News Check",      "https://tvnewscheck.com/business/feed",            "sports"),
    ("TechCrunch",         "https://techcrunch.com/feed/",                     "technology"),
    ("VentureBeat",        "https://venturebeat.com/feed/",                    "technology"),
    ("The Verge",          "https://www.theverge.com/rss/index.xml",           "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, */*"
}

def clean(text):
    if not text: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(text))).strip()

def fetch_feed(source, url, cat):
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code != 200: return items

        feed = feedparser.parse(r.content)
        now = datetime.now()

        for e in feed.entries[:25]:
            title = clean(e.get("title", ""))
            if len(title) < 30: continue

            summary = clean(e.get("summary") or e.get("description", ""))
            if not is_content_appropriate(title, summary): continue

            link = e.get("link", "")
            pub = now
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(e, k, None)
                if val:
                    try: pub = datetime(*val[:6])
                    except: pass
                    break

            ptype, badge, prio = classify_article(title, summary, cat)
            if ptype == "IRRELEVANT": continue

            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": cat,
                "badge": badge,
                "prio": prio,
                "score": calculate_relevance_score(title, summary, cat),
                "is_high": ptype == "HIGH"
            })
    except:
        pass
    return items

@st.cache_data(ttl=240, show_spinner=False)
def load_data():
    cats = {"telco":[], "ott":[], "sports":[], "technology":[], "highlights":[]}

    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = [ex.submit(fetch_feed, s, u, c) for s,u,c in RSS_FEEDS]
        for f in as_completed(futures):
            for item in f.result():
                cats[item["category"]].append(item)
                if item["is_high"] and (datetime.now() - item["pub"]).days <= 45:
                    cats["highlights"].append(item)

    # Deduplicate everywhere
    for k in cats:
        seen = set()
        unique = []
        for item in cats[k]:
            key = hashlib.md5(
                re.sub(r'\W+', '', (item["title"] + item["summary"]).lower()).encode()
            ).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        cats[k] = unique

    # Sort & limit
    for k in ["telco","ott","sports","technology"]:
        cutoff = datetime.now() - timedelta(days=10)
        cats[k] = [x for x in cats[k] if x["pub"] >= cutoff]
        cats[k].sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))
        cats[k] = cats[k][:6]

    # Highlights: Evergent/competitor first, then newest high-score
    cats["highlights"].sort(key=lambda x: (
        0 if x["is_high"] else 1,
        -x["score"],
        -x["pub"].timestamp()
    ))
    cats["highlights"] = cats["highlights"][:10]

    return cats

def time_ago(dt):
    secs = (datetime.now() - dt).total_seconds()
    if secs < 3600:    return "Now", "hot"
    if secs < 21600:   return f"{int(secs//3600)}h", "hot"
    if secs < 86400:   return f"{int(secs//3600)}h", "warm"
    return f"{int(secs//86400)}d", "normal"

# ─────────────────────────────────────────────────────────────────────────────
# UI – MODERN & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }

    .header {
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(12px);
        padding: 2.2rem 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 1.5rem 0 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .title {
        font-size: 3.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a5b4fc, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 1.15rem;
        color: #cbd5e1;
        margin-top: 0.6rem;
        font-weight: 500;
    }

    .highlight-box {
        background: rgba(30, 41, 59, 0.92);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    .highlight-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e0f2fe;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .highlight-item {
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        background: rgba(59, 69, 94, 0.4);
        border-radius: 10px;
        border-left: 4px solid #6366f1;
        transition: all 0.2s ease;
    }

    .highlight-item:hover {
        background: rgba(79, 89, 114, 0.55);
        transform: translateX(4px);
    }

    .section-header {
        font-size: 1.35rem;
        font-weight: 700;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
    }

    .section-body {
        background: rgba(30, 41, 59, 0.88);
        border-radius: 0 0 12px 12px;
        padding: 1.2rem;
        min-height: 420px;
        overflow-y: auto;
    }

    .news-card {
        background: rgba(59, 69, 94, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 0.9rem;
        transition: all 0.22s ease;
    }

    .news-card:hover {
        background: rgba(79, 89, 114, 0.6);
        border-color: #818cf8;
        transform: translateY(-2px);
    }

    .news-title {
        color: #e0f2fe;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 0.5rem;
    }

    .news-title:hover { color: #c7d2fe; }

    .news-meta {
        font-size: 0.82rem;
        color: #94a3b8;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .time-hot   { color: #f87171; font-weight: 600; }
    .time-warm  { color: #fb923c; font-weight: 600; }
    .time-normal{ color: #94a3b8; }

    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="title">Global Telecom & OTT Stellar Nexus</div>
    <div class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading latest intelligence…"):
    data = load_data()

# ── HIGHLIGHTS ──
st.markdown('<div class="highlight-box">', unsafe_allow_html=True)

st.markdown('<div class="highlight-title">🚀 STRATEGIC HITS</div>', unsafe_allow_html=True)
for item in [x for x in data["highlights"] if x["is_high"]][:5]:
    tago, cls = time_ago(item["pub"])
    st.markdown(f"""
    <div class="highlight-item">
        <strong>{item["badge"]} {html.escape(item["title"])}</strong><br>
        <span class="{cls}">{tago}</span> • {html.escape(item["source"])}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="highlight-title" style="margin-top:2rem;">⚡ PULSE</div>', unsafe_allow_html=True)
for item in data["highlights"][:6]:
    if item["is_high"]: continue  # already shown above
    tago, cls = time_ago(item["pub"])
    st.markdown(f"""
    <div class="highlight-item">
        <strong>{item["badge"]} {html.escape(item["title"])}</strong><br>
        <span class="{cls}">{tago}</span> • {html.escape(item["source"])}
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── SECTIONS ──
cols = st.columns(4)
section_cfg = {
    "telco":      {"name":"TELCO OSS/BSS",      "color":"#ec4899", "icon":"📡"},
    "ott":        {"name":"OTT & STREAMING",    "color":"#a78bfa", "icon":"📺"},
    "sports":     {"name":"SPORTS MEDIA",       "color":"#34d399", "icon":"🏆"},
    "technology": {"name":"AI & TECHNOLOGY",    "color":"#fb923c", "icon":"⚡"},
}

for idx, (cat, cfg) in enumerate(section_cfg.items()):
    with cols[idx]:
        st.markdown(f"""
        <div class="section-header" style="background: {cfg['color']};">
            {cfg['icon']} {cfg['name']}
        </div>
        <div class="section-body">
        """, unsafe_allow_html=True)

        items = data.get(cat, [])
        if not items:
            st.markdown("<div style='text-align:center; color:#94a3b8; padding:80px 0;'>Monitoring...</div>", unsafe_allow_html=True)
        else:
            for item in items:
                tago, cls = time_ago(item["pub"])
                st.markdown(f"""
                <div class="news-card">
                    <a href="{html.escape(item['link'])}" target="_blank" class="news-title">
                        {item['badge']} {html.escape(item['title'])}
                    </a>
                    <div class="news-meta">
                        <span class="{cls}">{tago}</span>
                        <span>•</span>
                        <span>{html.escape(item['source'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center; color:#cbd5e1; margin:3rem 0; padding:1.5rem; background:rgba(15,23,42,0.8); border-radius:12px;">
    <strong>AI Intelligence Active</strong>  • 
    Articles: {sum(len(data[c]) for c in section_cfg)}  • 
    Last update: {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# Keep alive
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

@st.fragment(run_every=300)
def keep_alive():
    load_data.clear()      # optional – force refresh cache
    st.empty()

keep_alive()
