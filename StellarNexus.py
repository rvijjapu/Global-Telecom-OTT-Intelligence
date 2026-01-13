import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & BASIC SETUP
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌐 Telecom & OTT Intelligence Nexus",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL PROFESSIONAL STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; font-family: 'Segoe UI', sans-serif; }
    .header { background: rgba(10, 25, 47, 0.92); color: white; padding: 2rem; text-align: center; border-radius: 0 0 24px 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); margin-bottom: 2rem; }
    .title { font-size: 3.2rem; font-weight: 800; margin: 0; letter-spacing: -1px; }
    .subtitle { font-size: 1.3rem; opacity: 0.9; margin-top: 0.6rem; }
    .section { background: rgba(255,255,255,0.96); border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.15); margin-bottom: 2.5rem; border: 1px solid #e2e8f0; }
    .section-header { padding: 1.2rem 1.5rem; font-size: 1.35rem; font-weight: 700; color: white; display: flex; align-items: center; gap: 12px; }
    .pink { background: linear-gradient(135deg, #c026d3, #9f1239); }
    .purple { background: linear-gradient(135deg, #7c3aed, #5b21b6); }
    .green { background: linear-gradient(135deg, #059669, #047857); }
    .orange { background: linear-gradient(135deg, #ea580c, #c2410c); }
    .content { padding: 1.2rem; max-height: 580px; overflow-y: auto; }
    .card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.1rem; margin-bottom: 1rem; transition: all 0.25s ease; }
    .card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); background: #f1f5f9; }
    .priority { background: linear-gradient(135deg, #fefce8, #fef3c7); border: 2px solid #fbbf24; }
    .title-link { color: #1e40af; font-weight: 600; font-size: 1.05rem; text-decoration: none; display: block; margin-bottom: 0.5rem; line-height: 1.35; }
    .title-link:hover { color: #1d4ed8; text-decoration: underline; }
    .meta { font-size: 0.82rem; color: #64748b; display: flex; gap: 10px; flex-wrap: wrap; }
    .hot { color: #dc2626; font-weight: 700; }
    .warm { color: #ea580c; font-weight: 700; }
    .normal { color: #64748b; }
    .status { background: rgba(16, 185, 129, 0.15); color: #065f46; padding: 0.8rem 1.2rem; border-radius: 12px; margin: 1rem 0; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# EVERGENT CLIENTS + COMPETITORS + KEYWORDS (very comprehensive)
# ──────────────────────────────────────────────────────────────────────────────
EVERGENT_CLIENTS = {
    "Astro": ["astro", "astro malaysia", "sooka", "njoi"],
    "FOX": ["fox", "fox sports", "fox corporation"],
    "AT&T": ["at&t", "att", "directv"],
    "NBA": ["nba", "national basketball"],
    "Shahid": ["shahid", "shahid vip"],
    "Sony": ["sony", "sonyliv", "sony pictures"],
    "BBC": ["bbc", "bbc iplayer"],
    "Sky": ["sky", "sky uk", "sky nz"],
    "FanDuel": ["fanduel"],
    "Bally Sports": ["bally sports"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi"],
    # ... add more as needed
}

COMPETITORS = {
    "Netcracker": ["netcracker", "nec netcracker"],
    "Amdocs": ["amdocs"],
    "Matrixx": ["matrixx"],
    "CSG": ["csg"],
    "Oracle": ["oracle communications"],
    "Ericsson": ["ericsson"],
    "Nokia": ["nokia"],
}

CRITICAL_KEYWORDS = [
    "merger", "acquisition", "deal", "partnership", "contract", "billion", "million",
    "oss", "bss", "billing", "charging", "monetization", "5g", "convergent", "revenue",
    "subscriber", "rights", "broadcast", "streaming", "platform", "launch", "expansion"
]

JUNK_KEYWORDS = [
    "coupon", "code", "discount", "sale", "offer", "promo", "voucher", "deal of the day",
    "black friday", "cyber monday", "flash sale", "limited time", "save", "% off",
    "giveaway", "contest", "win", "free trial", "sign up", "subscribe now", "shop now",
    "buy now", "best price", "clearance", "bogo"
]

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS - Focused on quality sources
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "color": "pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "color": "purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "color": "green"},
    "technology": {"icon": "⚡", "name": "AI & TECH", "color": "orange"},
}

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def clean(text):
    if not text:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(text))).strip()

def is_junk(title, summary=""):
    text = (title + " " + summary).lower()
    return any(term in text for term in JUNK_KEYWORDS)

def has_priority_content(title, summary=""):
    text = (title + " " + summary).lower()
    return any(kw in text for kw in CRITICAL_KEYWORDS)

def fetch_feed(source_name, url, category):
    items = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return items

        feed = feedparser.parse(resp.content)
        cutoff = datetime.now() - timedelta(days=7)

        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 30:
                continue

            summary = clean(entry.get("summary", title))

            if is_junk(title, summary):
                continue

            if not has_priority_content(title, summary):
                continue

            pub_date = None
            for key in ("published_parsed", "updated_parsed"):
                val = getattr(entry, key, None)
                if val:
                    try:
                        pub_date = datetime(*val[:6])
                        break
                    except:
                        pass

            if not pub_date or pub_date < cutoff:
                continue

            items.append({
                "title": title,
                "link": entry.get("link", "#"),
                "pub": pub_date,
                "source": source_name,
                "category": category,
                "priority": True  # All passed articles are priority
            })
    except:
        pass

    return items

@st.cache_data(ttl=600)
def load_all():
    categorized = {k: [] for k in SECTIONS}

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [
            executor.submit(fetch_feed, name, url, cat)
            for name, url, cat in RSS_FEEDS
        ]

        for future in as_completed(futures):
            try:
                articles = future.result()
                if articles:
                    categorized[articles[0]["category"]].extend(articles)
            except:
                continue

    # Sort: newest first
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
        categorized[cat] = categorized[cat][:12]

    return categorized

def get_time_badge(dt):
    hours = int((datetime.now() - dt).total_seconds() / 3600)
    if hours < 2: return "🟢 Now", "hot"
    if hours < 12: return f"🟠 {hours}h", "warm"
    return f"🔵 {hours//24}d", "normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDER SECTION - Beautiful & Contained
# ──────────────────────────────────────────────────────────────────────────────
def render_section(category, articles):
    cfg = SECTIONS[category]
    header = f"""
    <div class="section-header {cfg['color']}">
        {cfg['icon']} {cfg['name']}
    </div>
    """

    if not articles:
        content = '<div style="padding:120px 20px;text-align:center;color:#94a3b8;font-size:1.1rem;">No critical news in last 7 days</div>'
    else:
        content = ""
        for art in articles:
            time_str, cls = get_time_badge(art["pub"])
            title = html.escape(art["title"])
            link = html.escape(art["link"])
            source = html.escape(art["source"])

            content += f"""
            <div class="card">
                <a href="{link}" target="_blank" class="title-link">{title}</a>
                <div class="meta">
                    <span class="{cls}">{time_str}</span>
                    <span>•</span>
                    <span>{source}</span>
                </div>
            </div>
            """

    full = f"""
    <div class="section">
        {header}
        <div class="news-container">{content}</div>
    </div>
    """

    components.html(full, height=660, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="title">Global Telecom & OTT Intelligence Nexus</div>
    <div class="subtitle">Real-time Critical News • Clients • Competitors • OSS/BSS • Deals • January 2026</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading high-impact intelligence (no promos, no junk)..."):
    data = load_all()

total_articles = sum(len(v) for v in data.values())

st.markdown(f"""
<div class="status">
    Loaded {total_articles} high-priority articles • Last 7 days • Zero promotions/coupons
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    with cols[idx]:
        render_section(cat, data.get(cat, []))

st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.9rem; margin:3rem 0 2rem;">
    Powered by Real-time RSS Intelligence • Focused on EVERGENT ecosystem
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)
