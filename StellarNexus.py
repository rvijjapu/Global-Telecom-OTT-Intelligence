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

# Health check
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
# EVERGENT DATA – PASTE YOUR FULL DICTIONARIES HERE
# ─────────────────────────────────────────────────────────────────────────────

EVERGENT_CLIENTS = {
    # Example – replace with your full list
    "Astro": ["astro", "sooka", "njoi"],
    "Shahid": ["shahid", "mbc shahid"],
    "AT&T": ["at&t", "att", "directv"],
    "NBA": ["nba", "national basketball"],
    # "NextClient": ["var1", "var2"],
    # ...
}

COMPETITORS = {
    # Example – replace with your full list
    "Amdocs": ["amdocs"],
    "Netcracker": ["netcracker"],
    "CSG": ["csg"],
    # ...
}

TOP_TELCOS = {
    # Example – replace with your full flat list
    "Verizon": ["verizon", "verizon wireless"],
    "AT&T": ["at&t", "att"],
    "Reliance Jio": ["jio", "reliance jio"],
    # ...
}

# ─────────────────────────────────────────────────────────────────────────────
# SCORING SIGNALS (your original – keep or tune)
# ─────────────────────────────────────────────────────────────────────────────
TELCO_SIGNALS = {
    "tier1": ["5g monetization", "convergent billing", "digital bss", "oss transformation",
              "real-time charging", "network slicing", "api-based billing"],
    "tier2": ["bss", "oss", "billing platform", "charging system", "revenue management"],
    "tier3": ["telecom", "telco", "operator"],
    "negative": ["oil", "gas", "petroleum", "insurance", "banking", "semiconductor", "mining"]
}

OTT_SIGNALS = {
    "tier1": ["subscriber growth", "arpu", "streaming platform", "content deal", "ott expansion"],
    "tier2": ["streaming", "ott", "video platform", "subscription", "svod", "avod"],
    "tier3": ["media", "entertainment", "video"],
    "negative": ["cinema release", "box office", "movie review", "celebrity gossip", "red carpet"]
}

SPORTS_SIGNALS = {
    "tier1": ["media rights deal", "broadcasting rights", "sports streaming platform", "league partnership"],
    "tier2": ["sports media", "broadcasting", "sports streaming", "fan engagement"],
    "tier3": ["sports", "football", "basketball"],
    "negative": ["player injury", "match score", "fantasy tips", "betting odds", "transfer gossip"]
}

AI_SIGNALS = {
    "tier1": ["ai platform launch", "generative ai", "enterprise ai", "saas platform"],
    "tier2": ["artificial intelligence", "cloud computing", "enterprise software", "api"],
    "tier3": ["technology", "software", "digital"],
    "negative": ["semiconductor", "chip fabrication", "crypto mining", "nft"]
}

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

    # Boosts (no display – only for ranking)
    if any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values()):
        score += 80

    if any(any(v in content for v in vs) for vs in COMPETITORS.values()):
        score += 60

    if any(any(v in content for v in vs) for vs in TOP_TELCOS.values()):
        score += 30

    action_keywords = [
        "acquisition", "merger", "partnership", "deal", "expansion", "launches",
        "extension", "investment", "strategic", "wins", "award", "deploy", "scale",
        "growth", "churn reduction", "monetization", "subscriber growth", "arpu",
        "billing transformation", "oss transformation", "5g monetization",
        "real-time charging", "revenue management", "content deal", "media rights"
    ]
    score += sum(20 for kw in action_keywords if kw in content)

    return min(score, 100)

def classify_article(title, summary, category):
    content = f"{title} {summary}".lower()
    score = calculate_relevance_score(title, summary, category)

    if score < 50:
        return "IRRELEVANT", "", 999

    if any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values()):
        return "CLIENT", "🌟", 0

    if any(any(v in content for v in vs) for vs in COMPETITORS.values()):
        return "COMPETITOR", "⚠️", 1

    badges = {
        "telco":      ("TELCO",  "📡", 5),
        "ott":        ("OTT",    "📺", 6),
        "sports":     ("SPORTS", "🏆", 7),
        "technology": ("TECH",   "⚡", 8)
    }

    tag, icon, prio = badges.get(category, ("", "", 999))
    return tag, icon, prio

# ─────────────────────────────────────────────────────────────────────────────
# RSS FEEDS – FIXED SYNTAX
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com",       "https://www.telecoms.com/feed",                    "telco"),
    ("Light Reading",      "https://www.lightreading.com/rss/simple",          "telco"),
    ("Fierce Telecom",     "https://www.fierce-network.com/rss.xml",           "telco"),
    ("RCR Wireless",       "https://www.rcrwireless.com/feed",                 "telco"),
    ("Mobile World Live",  "https://www.mobileworldlive.com/feed/",            "telco"),
    ("Variety",            "https://variety.com/feed/",                        "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/",          "ott"),
    ("Deadline",           "https://deadline.com/feed/",                       "ott"),
    ("Streaming Media",    "https://www.streamingmedia.com/rss",               "ott"),
    ("ESPN",               "https://www.espn.com/espn/rss/news",               "sports"),
    ("SportsPro",          "https://www.sportspromedia.com/feed/",             "sports"),
    ("SportBusiness",      "https://www.sportbusiness.com/feed/",              "sports"),
    ("TV News Check",      "https://tvnewscheck.com/business/feed",            "sports"),
    ("TechCrunch",         "https://techcrunch.com/feed/",                     "technology"),
    ("VentureBeat",        "https://venturebeat.com/feed/",                    "technology"),
    ("The Verge",          "https://www.theverge.com/rss/index.xml",           "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ─────────────────────────────────────────────────────────────────────────────
# FEED PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return items

        feed = feedparser.parse(resp.content)
        NOW = datetime.now()

        for entry in feed.entries[:25]:
            title = clean(entry.get("title", ""))
            if len(title) < 25:
                continue

            summary = clean(entry.get("summary") or entry.get("description", ""))
            if not is_content_appropriate(title, summary):
                continue

            link = entry.get("link", "")

            pub = NOW
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break

            tag, badge, prio = classify_article(title, summary, category)
            if tag == "IRRELEVANT":
                continue

            score = calculate_relevance_score(title, summary, category)

            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "tag": tag,
                "badge": badge,
                "prio": prio,
                "score": score,
                "is_priority": tag in ["CLIENT", "COMPETITOR"] or score >= 75
            })
    except Exception:
        pass

    return items

@st.cache_data(ttl=240, show_spinner=False)
def load_feeds():
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": [],
        "highlights": []
    }

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]

        for future in as_completed(futures):
            for item in future.result():
                categorized[item["category"]].append(item)
                if item["is_priority"] and (datetime.now() - item["pub"]).days <= 45:
                    categorized["highlights"].append(item)

    # Deduplication
    for key in categorized:
        seen = set()
        unique = []
        for item in categorized[key]:
            norm = re.sub(r'\W+', '', (item["title"] + item["summary"]).lower())
            h = hashlib.md5(norm.encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)
        categorized[key] = unique

    # Sort & limit
    for cat in ["telco", "ott", "sports", "technology"]:
        cutoff = datetime.now() - timedelta(days=10)
        categorized[cat] = [x for x in categorized[cat] if x["pub"] >= cutoff]
        categorized[cat].sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))
        categorized[cat] = categorized[cat][:6]

    # Highlights: priority first
    categorized["highlights"].sort(key=lambda x: (
        0 if x["is_priority"] else 1,
        -x["score"],
        -x["pub"].timestamp()
    ))
    categorized["highlights"] = categorized["highlights"][:12]

    return categorized

def time_ago(dt):
    secs = (datetime.now() - dt).total_seconds()
    if secs < 3600:    return "Now", "time-hot"
    if secs < 21600:   return f"{int(secs//3600)}h", "time-hot"
    if secs < 86400:   return f"{int(secs//3600)}h", "time-warm"
    return f"{int(secs//86400)}d", "time-normal"

# ─────────────────────────────────────────────────────────────────────────────
# STYLING – CLEAN & MODERN
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
        backdrop-filter: blur(10px);
        padding: 2rem 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 1.5rem 0 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a5b4fc, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #cbd5e1;
        margin-top: 0.5rem;
    }

    .highlights-container {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 2.5rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e0f2fe;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .highlight-card {
        background: rgba(59, 69, 94, 0.5);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
        border-left: 4px solid #6366f1;
        transition: all 0.2s;
    }

    .highlight-card:hover {
        background: rgba(79, 89, 114, 0.65);
        transform: translateX(4px);
    }

    .card-title {
        color: #e0f2fe;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .card-meta {
        font-size: 0.82rem;
        color: #94a3b8;
    }

    .time-hot   { color: #f87171; font-weight: 600; }
    .time-warm  { color: #fb923c; font-weight: 600; }
    .time-normal{ color: #94a3b8; }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin: 0;
    }

    .section-body {
        background: rgba(30, 41, 59, 0.88);
        border-radius: 0 0 12px 12px;
        padding: 1.2rem;
        min-height: 400px;
    }

    .news-card {
        background: rgba(59, 69, 94, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s;
    }

    .news-card:hover {
        background: rgba(79, 89, 114, 0.65);
        border-color: #818cf8;
    }

    .news-link {
        color: #c7d2fe;
        font-size: 1.02rem;
        font-weight: 600;
        text-decoration: none;
        display: block;
        margin-bottom: 0.4rem;
    }

    .news-link:hover { color: #e0f2fe; }

    .news-meta {
        font-size: 0.8rem;
        color: #94a3b8;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="title">Global Telecom & OTT Stellar Nexus</div>
    <div class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading latest intelligence..."):
    data = load_feeds()

# ── HIGHLIGHTS ──
st.markdown('<div class="highlights-container">', unsafe_allow_html=True)

st.markdown('<div class="section-title">🚀 Strategic Hits</div>', unsafe_allow_html=True)
for item in [x for x in data["highlights"] if x["is_priority"]][:6]:
    tago, cls = time_ago(item["pub"])
    st.markdown(f"""
    <div class="highlight-card">
        <div class="card-title">{item["badge"]} {html.escape(item["title"])}</div>
        <div class="card-meta">
            <span class="{cls}">{tago}</span> • {html.escape(item["source"])}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title" style="margin-top:1.8rem;">⚡ Pulse</div>', unsafe_allow_html=True)
for item in data["highlights"][:8]:
    if item["is_priority"]: continue
    tago, cls = time_ago(item["pub"])
    st.markdown(f"""
    <div class="highlight-card">
        <div class="card-title">{item["badge"]} {html.escape(item["title"])}</div>
        <div class="card-meta">
            <span class="{cls}">{tago}</span> • {html.escape(item["source"])}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN SECTIONS ──
cols = st.columns(4)

sections = {
    "telco":      {"name": "TELCO OSS/BSS",  "color": "#ec4899", "icon": "📡"},
    "ott":        {"name": "OTT & STREAMING","color": "#a78bfa", "icon": "📺"},
    "sports":     {"name": "SPORTS MEDIA",   "color": "#34d399", "icon": "🏆"},
    "technology": {"name": "AI & TECHNOLOGY","color": "#fb923c", "icon": "⚡"},
}

for idx, (cat, cfg) in enumerate(sections.items()):
    with cols[idx]:
        st.markdown(f"""
        <div class="section-header" style="background:{cfg['color']};">
            {cfg['icon']} {cfg['name']}
        </div>
        <div class="section-body">
        """, unsafe_allow_html=True)

        items = data.get(cat, [])
        if not items:
            st.markdown('<div style="text-align:center; color:#94a3b8; padding:100px 0;">Monitoring...</div>', unsafe_allow_html=True)
        else:
            for item in items:
                tago, cls = time_ago(item["pub"])
                st.markdown(f"""
                <div class="news-card">
                    <a href="{html.escape(item['link'])}" target="_blank" class="news-link">
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
    <strong>AI Intelligence Active</strong>  •  Articles: {sum(len(data[c]) for c in sections)}  • 
    Last update: {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

@st.fragment(run_every=300)
def keep_alive():
    st.empty()

keep_alive()
