import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import html
import time

# ────────────────────────────────────────────────
# 🔐 CEO TOKEN SECURITY GATE
# ────────────────────────────────────────────────
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except (FileNotFoundError, KeyError):
    st.error("🔧 CEO_ACCESS_TOKEN missing in secrets.toml or Streamlit Cloud")
    st.stop()

provided_token = st.query_params.get("token", [""])[0]
if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized – Invalid or missing token")
    st.info("Use ?token=your_token in URL")
    st.stop()

# Simple rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0
if time.time() - st.session_state.last_access < 2:
    st.warning("⏱ Slow down – too many requests")
    st.stop()
st.session_state.last_access = time.time()

# ────────────────────────────────────────────────
# PAGE CONFIG & KEEP-ALIVE
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus – 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.fragment(run_every=600)
def keep_alive():
    st.markdown("")

# ────────────────────────────────────────────────
# PREMIUM CSS (Merged & Optimized)
# ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    .dark-blue-text { color: #0a192f !important; font-weight: 800 !important; }
    .header-container {
        background: rgba(255,255,255,0.95);
        padding: 1.4rem;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
        margin: 1rem 1.5rem 2rem;
        border-bottom: 5px solid #3b82f6;
        backdrop-filter: blur(8px);
        text-align: center;
    }
    .main-title { font-size: 2.6rem; color: #1e40af; margin: 0; }
    .subtitle { font-size: 1.15rem; color: #475569; margin-top: 0.5rem; }
    .hero-container {
        background: rgba(255,255,255,0.96);
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 2rem;
    }
    .hero-title { 
        font-size: 1.9rem; font-weight: 800; color: #1e40af; 
        border-left: 6px solid #1e40af; padding-left: 14px; margin-bottom: 1.2rem;
    }
    .hero-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.4rem;
        border: 1px solid #e2e8f0;
        min-height: 210px;
    }
    .section-card {
        background: rgba(255,255,255,0.97);
        border-radius: 14px;
        padding: 1.6rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.14);
        min-height: 520px;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.35rem; font-weight: 800;
        padding-bottom: 10px;
        border-bottom: 4px solid;
        margin-bottom: 1.2rem;
        text-transform: uppercase;
    }
    .news-card, .news-card-priority {
        background: #fdfdfd;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        transition: all 0.25s;
    }
    .news-card:hover, .news-card-priority:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.1);
    }
    .news-card-priority {
        background: #fffbeb;
        border: 2px solid #fbbf24;
    }
    .news-title {
        color: #1d4ed8;
        font-weight: 600;
        font-size: 0.96rem;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
    }
    .news-title:hover { color: #1e40af; text-decoration: underline; }
    .news-summary {
        font-size: 0.84rem;
        color: #4b5563;
        line-height: 1.45;
        margin-top: 4px;
    }
    .news-meta {
        font-size: 0.78rem;
        color: #6b7280;
        display: flex;
        gap: 8px;
        margin-top: 6px;
    }
    .time-hot { color: #dc2626; font-weight: 700; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #6b7280; }
    .loading-container {
        text-align: center;
        padding: 180px 0;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# CLIENT & COMPETITOR LISTS (from your provided data)
# ────────────────────────────────────────────────
EVERGENT_CLIENTS = {
    "Astro": ["astro", "astro malaysia", "sooka", "njoi"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "Aha": ["aha", "aha video", "aha ott"],
    "Sky": ["sky nz", "sky new zealand", "sky tv"],
    "AT&T": ["at&t", "att", "directv"],
    "Singtel": ["singtel"],
    "Globe": ["globe telecom", "globe philippines"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv"],
    # Add more if needed...
}

COMPETITORS = {
    "Netcracker": ["netcracker", "nec netcracker"],
    "Amdocs": ["amdocs"],
    "CSG": ["csg"],
    "MATRIXX": ["matrixx"],
    "Ericsson": ["ericsson"],
    "Nokia": ["nokia"],
    "Oracle": ["oracle communications", "oracle telecom"],
}

# Combined keywords for Telco OSS/BSS strict filtering
TELCO_FILTER_KEYWORDS = set()
for d in [EVERGENT_CLIENTS, COMPETITORS]:
    for names in d.values():
        TELCO_FILTER_KEYWORDS.update(names)

# ────────────────────────────────────────────────
# RSS FEEDS (same as before)
# ────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Netcracker Press", "https://rss.app/feeds/oyAS1q31oAma1iDX.xml"),
    ("Amdocs", "https://rss.app/feeds/rszN8UooJxRHd9RT.xml"),  # example
    # Add more as needed...
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco OSS/BSS", "color": "#db2777"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "color": "#7c3aed"},
    "sports": {"icon": "🏆", "name": "Sports Media", "color": "#059669"},
    "technology": {"icon": "⚡", "name": "AI & Techwatch", "color": "#ea580c"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco", "Light Reading": "telco", "Fierce Telecom": "telco",
    "RCR Wireless": "telco", "Mobile World Live": "telco", "ET Telecom": "telco",
    "Netcracker Press": "telco", "Amdocs": "telco",
    # OTT, Sports, Tech would need their own feeds...
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(text):
    if not text: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(text))).strip()

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200: return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=5)  # slightly longer window for quality
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 25: continue
            summary = clean(entry.get("summary", "") or entry.get("description", ""))
            link = entry.get("link", "")
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                if val := getattr(entry, k, None):
                    try: pub = datetime(*val[:6]); break
                    except: pass
            if not pub or pub < CUTOFF: continue

            combined = (title + " " + summary).lower()
            category = SOURCE_CATEGORY_MAP.get(source, "technology")

            # Special strict filter for Telco section
            is_telco_relevant = category == "telco" and any(kw in combined for kw in TELCO_FILTER_KEYWORDS)

            if category != "telco" or is_telco_relevant:
                item = {
                    "title": title, "link": link, "pub": pub,
                    "source": source, "summary": summary,
                    "category": category
                }
                # Priority boost for Evergent client or strong competitor mention
                if any(kw in combined for kw in ["evergent", "astro", "shahid", "aha", "netcracker", "amdocs", "matrixx"]):
                    item["priority"] = True
                items.append(item)
    except:
        pass
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {k: [] for k in SECTIONS}
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, src, url) for src, url in RSS_FEEDS]
        for future in as_completed(futures):
            for item in future.result():
                categorized[item["category"]].append(item)

    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    return categorized

def get_time_label(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_news_items(items):
    html = ""
    for item in items:
        time_str, time_cls = get_time_label(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        safe_sum = html.escape(item["summary"][:140] + "..." if len(item["summary"]) > 140 else item["summary"])
        card_cls = "news-card-priority" if item.get("priority", False) else "news-card"
        html += f'''
        <div class="{card_cls}">
            <a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
            <div class="news-summary">{safe_sum}</div>
            <div class="news-meta">
                <span class="{time_cls}">{time_str}</span>
                <span>•</span>
                <span>{safe_source}</span>
            </div>
        </div>
        '''
    return html if html else '<div style="text-align:center; color:#9ca3af; padding:40px 0;">No recent matching news</div>'

# ────────────────────────────────────────────────
# LOADING SCREEN
# ────────────────────────────────────────────────
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
    <div class="loading-container">
        <h1 class="dark-blue-text" style="font-size:3.2rem;">Igniting 2026 Intelligence...</h1>
        <p style="font-size:1.3rem; color:#1e40af; opacity:0.9;">Filtering global OSS/BSS & OTT signals – please wait</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1.6)

placeholder.empty()

# ────────────────────────────────────────────────
# MAIN DASHBOARD
# ────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence – January 2026</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 minutes
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 300:
    st.session_state.last_refresh = time.time()
    st.rerun()

data = load_feeds()

# Highlights Section (static + dynamic hints)
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 2026 STRATEGIC HIGHLIGHTS</div>
    <div style="display:flex; gap:24px; flex-wrap:wrap;">
        <div class="hero-box" style="flex:1;">
            <div style="font-weight:800; color:#10b981; font-size:1.15rem; margin-bottom:10px;">🟢 KEY MOVES</div>
            <div style="line-height:1.7; color:#1f2937;">
                • Globe Telecom expands Netcracker OSS partnership<br>
                • Singtel advances enterprise service layer transformation<br>
                • Astro continues BSS modernization success story
            </div>
        </div>
        <div class="hero-box" style="flex:1;">
            <div style="font-weight:800; color:#f97316; font-size:1.15rem; margin-bottom:10px;">🟠 INDUSTRY PULSE</div>
            <div style="line-height:1.7; color:#1f2937;">
                • Agentic AI adoption accelerating in BSS operations<br>
                • 5G monetization & charging platforms under pressure<br>
                • Legacy OSS replacement wave gaining momentum in APAC
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Four Column Dashboard
cols = st.columns(4)
cat_order = ["telco", "ott", "sports", "technology"]

for i, cat in enumerate(cat_order):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    # For telco → only the filtered ones are already present
    with cols[i]:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-header" style="color:{sec['color']}; border-color:{sec['color']};">
                {sec['icon']} {sec['name']}
            </div>
            {render_news_items(items[:10])}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<p style="text-align:center; color:#e5e7eb; padding:2rem 0; font-size:0.9rem;">
    Live Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST  |  
    Filtered for Evergent Clients + Key Telcos + Competitors
</p>
""", unsafe_allow_html=True)
