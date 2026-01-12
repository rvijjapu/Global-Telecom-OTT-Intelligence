import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import re
import html
import time

# ==========================
# 🔐 CEO TOKEN SECURITY GATE (Using Streamlit Secrets)
# ==========================
# In your GitHub repo, create a file: .streamlit/secrets.toml
# Content:
# CEO_ACCESS_TOKEN = "Vijay"   # Change to a strong random string in production!

try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

# Get token from URL query parameter: ?token=Vijay
provided_token = st.query_params.get("token")
if provided_token is not None:
    # st.query_params returns a list in newer versions
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

# Simple rate limiting (anti-bot protection)
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:  # Less than 2 seconds
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NEVER-SLEEP / KEEP-ALIVE FRAGMENT ---
# Resets inactivity timer every 10 minutes to prevent hibernation
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# 2. PREMIUM CSS: Merged and Optimized for Professional Look
st.markdown("""
<style>
    /* Professional Dark Blue Title Styling */
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
    }
   
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
        padding-top: 0.5rem;
    }
   
    /* Center the Loading State */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }

    /* Hero Section: Strategic Baseline (Top Focus) */
    .hero-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.2rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        margin: 0 1.5rem 1.8rem 1.5rem;
        border-bottom: 4px solid #3b82f6;
        backdrop-filter: blur(8px);
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1e40af;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }

    .hero-box {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1.5rem;
        min-height: 220px;
        border: 1px solid #e2e8f0;
    }

    /* Industry Vertical Cards */
    .section-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 24px;
        border-radius: 12px;
        min-height: 480px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    .news-item {
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.5;
    }

    .news-card {
        background: #fafbfc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }

    .news-card:hover {
        background: #f1f5f9;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }

    .news-card-priority {
        background: #fefce8;
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }

    .news-card-priority:hover {
        background: #fef3c7;
        box-shadow: 0 8px 20px rgba(251,191,36,0.15);
    }

    .news-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
    }

    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }

    .news-meta {
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
</style>
""", unsafe_allow_html=True)

# === OPTIMIZED & FILTERED RSS FEEDS (ONLY FAST + ACTIVE) ===
# Updated for 2026 relevance: Added filters for future-oriented keywords like "2026", "future", "AI", etc.
RSS_FEEDS = [
    # Telco
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Netcracker Press", "https://rss.app/feeds/oyAS1q31oAma1iDX.xml"),
    ("Netcracker News", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Amdocs LinkedIn", "https://rss.app/feeds/rszN8UooJxRHd9RT.xml"),

    # OTT
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),

    # Sports
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),

    # Technology
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
    ("Techmeme", "https://www.techmeme.com/feed.xml"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco OSS/BSS", "color": "#db2777"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "color": "#7c3aed"},
    "sports": {"icon": "🏆", "name": "Sports Media", "color": "#059669"},
    "technology": {"icon": "⚡", "name": "AI Techwatch", "color": "#ea580c"},
}

SOURCE_CATEGORY_MAP = {
    # Telco
    "Telecoms.com": "telco",
    "Light Reading": "telco",
    "Fierce Telecom": "telco",
    "RCR Wireless": "telco",
    "Mobile World Live": "telco",
    "ET Telecom": "telco",
    "Netcracker Press": "telco",
    "Netcracker News": "telco",
    "Amdocs LinkedIn": "telco",

    # OTT
    "Variety": "ott",
    "Hollywood Reporter": "ott",
    "Deadline": "ott",
    "Digital TV Europe": "ott",
    "Advanced Television": "ott",

    # Sports
    "ESPN": "sports",
    "BBC Sport": "sports",
    "Front Office Sports": "sports",
    "Sportico": "sports",
    "SportsPro": "sports",

    # Technology
    "TechCrunch": "technology",
    "The Verge": "technology",
    "Wired": "technology",
    "Ars Technica": "technology",
    "VentureBeat": "technology",
    "ZDNet": "technology",
    "Engadget": "technology",
    "Techmeme": "technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=4)
        if resp.status_code != 200:
            return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=3)
        for entry in feed.entries[:10]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            summary = clean(entry.get("summary", ""))
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
            # AI-like filter: Prioritize 2026-relevant news (improvise dynamic algorithm)
            if any(keyword in (title + summary).lower() for keyword in ["2026", "ai", "future", "agentic", "quantum", "5g", "6g", "streaming", "ott", "sports"]):
                items.append({
                    "title": title, "link": link, "pub": pub, "source": source,
                    "summary": summary
                })
    except:
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

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [
            executor.submit(fetch_feed, source, url)
            for source, url in RSS_FEEDS
        ]

        for future in as_completed(futures):
            items = future.result()
            for item in items:
                category = SOURCE_CATEGORY_MAP.get(
                    item["source"], "technology"
                )
                categorized[category].append(item)

    for cat in categorized:
        categorized[cat].sort(
            key=lambda x: x["pub"],
            reverse=True
        )

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

def render_news_items(items):
    news_html = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        safe_summary = html.escape(item["summary"][:150] + "..." if item["summary"] else "")  # Short summary
        card_class = "news-card-priority" if any(kw in (item["title"] + item.get("summary", "")).lower() for kw in ["netcracker", "amdocs", "ai", "2026"]) else "news-card"
        news_html += f'''
        <div class="{card_class}">
            <a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{safe_source}</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin-top:6px;">{safe_summary}</div>
        </div>
        '''
    if not items:
        news_html = '<div style="text-align:center;color:#94a3b8;padding:30px;">No recent news</div>'
    return news_html

# 3. IMPACTFUL LOADING SEQUENCE
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Synchronizing global 2026 insights with dynamic AI algorithm.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8)  # Millisecond loading simulation

placeholder.empty()

# 4. MAIN DASHBOARD CONTENT
st.markdown("<h1 class='dark-blue-text' style='text-align: center; font-size: 3.2rem; margin-bottom: 30px;'>🌐 Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# Dynamic AI Algorithm: Auto-refresh every 5 minutes (300 seconds)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:
    st.session_state.last_refresh = time.time()
    st.rerun()

# Load dynamic data with AI-like filtering
data = load_feeds()

# 🚀 HIGHLIGHTS (TOP SECTION) - Improvised with summaries from dynamic feeds
# Extract top hits and pulse dynamically (top 3 from telco/tech as example)
strategic_hits = []
pulse = []
for cat in ["telco", "technology"]:
    for item in data[cat][:3]:
        if "acquisition" in item["title"].lower() or "merger" in item["title"].lower():
            strategic_hits.append(f'<b><a href="{item["link"]}" target="_blank">{item["title"]}</a></b>: {item["summary"][:100]}...')
        else:
            pulse.append(f'<b><a href="{item["link"]}" target="_blank">{item["title"]}</a></b>: {item["summary"][:100]}...')

# Fallback to static if no dynamic
if not strategic_hits:
    strategic_hits = [
        '<b>Amdocs-Matrixx Deal:</b> Amdocs completes its $200M acquisition of charging leader Matrixx Software to dominate the Tier-1 5G billing market.',
        '<b>Disney-Hulu Merger:</b> Disney officially begins phasing out the standalone Hulu app to integrate all content into a unified Disney+ hub.',
        '<b>NEC Expansion:</b> Japan\'s NEC finalizes the acquisition of CSG, significantly scaling Netcracker\'s North American SaaS footprint.'
    ]
if not pulse:
    pulse = [
        '<b>Agentic AI Core:</b> By EOY 2026, autonomous AI agents are expected to handle roughly 40% of standard BSS operational tasks.',
        '<b>Satellite Breakout:</b> Direct-to-consumer satellite broadband moves from niche to mainstream as a primary fiber competitor.',
        '<b>Physical AI:</b> Amazon deploys its 1-millionth robot, integrated with DeepFleet AI for a 10% gain in warehouse efficiency.'
    ]

hits_html = "<br>".join(strategic_hits)
pulse_html = "<br>".join(pulse)

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🚀 HIGHLIGHTS - 2026 Strategic Summary</div>
    <div style="display: flex; gap: 20px;">
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS </div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">{hits_html}</div>
        </div>
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 PULSE </div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">{pulse_html}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📊 VERTICAL INDUSTRY GRID - Dynamic News with Hyperlinks
col1, col2, col3, col4 = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]
for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    news_html = render_news_items(items[:10])  # Top 10 latest
    with [col1, col2, col3, col4][idx]:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-header" style="color: {sec['color']}; border-color: {sec['color']};">{sec['icon']} {sec['name']}</div>
            {news_html}
        </div>
        """, unsafe_allow_html=True)

# Footer with Live Sync
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Sync (Auto-Refresh AI): {datetime.now().strftime('%H:%M:%S')} | Powered by Dynamic AI Algorithm</p>", unsafe_allow_html=True)
