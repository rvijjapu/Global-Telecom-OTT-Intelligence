import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib
import time

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
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
# EVERGENT PRIORITY KEYWORDS (expand as needed)
# ─────────────────────────────────────────────────────────────────────────────
EVERGENT_KEYWORDS = [
    "evergent", "evergent technologies", "astro", "sooka", "njoi", "shahid",
    "mbc shahid", "nba", "national basketball", "sonyliv", "sky nz", "bbc iplayer",
    "abs-cbn", "directv", "fox sports", "fox networks"
]

def is_evergent_related(title, summary):
    content = f"{title} {summary}".lower()
    return any(kw in content for kw in EVERGENT_KEYWORDS)

# ─────────────────────────────────────────────────────────────────────────────
# RSS FEEDS (your latest list)
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("Streaming Media", "https://www.streamingmedia.com/rss", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6)
        if resp.status_code != 200:
            return items

        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=7)  # only recent news

        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 25:
                continue

            summary = clean(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")

            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break

            if not pub or pub < CUTOFF:
                continue

            is_priority = is_evergent_related(title, summary)

            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "priority": is_priority
            })
    except Exception:
        pass

    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": []
    }

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]

        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)

    # Deduplicate + sort: Evergent priority first, then newest
    for cat in categorized:
        seen = set()
        unique = []
        for item in categorized[cat]:
            key = hashlib.md5(
                re.sub(r'\W+', '', (item["title"] + item["summary"]).lower()).encode()
            ).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(item)

        # Sort: priority first → newest
        unique.sort(key=lambda x: (
            0 if x["priority"] else 1,
            -x["pub"].timestamp()
        ))

        categorized[cat] = unique[:8]  # max 8 per section

    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    if not items:
        return '<div style="text-align:center;color:#94a3b8;padding:60px 0;">No recent high-impact news</div>'

    cards = []
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])

        card_class = "news-card-priority" if item["priority"] else "news-card"

        card = f'''
        <div class="{card_class}">
            <a href="{link}" target="_blank" class="news-title">{title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{source}</span>
            </div>
        </div>
        '''
        cards.append(card)

    return '<div class="col-body">' + ''.join(cards) + '</div>'

# ─────────────────────────────────────────────────────────────────────────────
# KEEP-ALIVE FRAGMENT
# ─────────────────────────────────────────────────────────────────────────────
@st.fragment(run_every=300)
def keep_alive():
    st.empty()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
# Loading screen
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:2.8rem; font-weight:800;">Igniting AI-powered intelligence...</h1>
            <p style="color:#64748b; font-size:1.2rem;">Synchronizing global news nodes</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.2)

placeholder.empty()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Highlights Section (static sample – you can make dynamic later)
st.markdown("""
<div class="hero-container">
    <div class="hero-title">HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">STRATEGIC HITS</div>
            <div class="hero-content">
                <b>Amdocs-MatriXX Deal:</b> Amdocs completes $200M acquisition of charging leader MatriXX to dominate Tier-1 5G billing.<br><br>
                <b>Disney-Hulu Integration:</b> Disney begins phasing out standalone Hulu app into unified Disney+ hub.<br><br>
                <b>NEC-CSG Acquisition:</b> NEC finalizes CSG acquisition, expanding Netcracker SaaS footprint.
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316;">PULSE</div>
            <div class="hero-content">
                <b>Agentic AI in BSS:</b> By EOY 2026, autonomous AI agents expected to handle 40% of standard BSS operations.<br><br>
                <b>Satellite Broadband Rise:</b> Direct-to-consumer satellite moves from niche to mainstream fiber competitor.<br><br>
                <b>Physical AI Milestone:</b> Amazon deploys 1-millionth robot with DeepFleet AI – 10% warehouse efficiency gain.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch real-time news
with st.spinner(""):
    data = load_feeds()

# Render News Columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS.get(cat, {"icon": "", "name": cat.upper(), "style": "col-header-purple"})
    items = data.get(cat, [])[:10]

    with cols[idx]:
        # Header
        st.markdown(f"""
        <div class="{sec['style']} col-header">
            {sec['icon']} {sec['name']}
        </div>
        """, unsafe_allow_html=True)

        # Body with priority ordering already done
        st.markdown(render_body(items), unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; color:rgba(255,255,255,0.85); font-size:0.85rem; margin-top:2.5rem; padding:1.5rem; background:linear-gradient(135deg,rgba(15,23,42,0.9),rgba(30,41,59,0.9)); border-radius:12px;">
    <strong>AI Intelligence Active</strong>  •  Auto-refresh every 5 minutes  •  Powered by Real-time Global Feeds
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
keep_alive()
