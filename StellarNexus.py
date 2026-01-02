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


st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === MINIMAL TOP SPACING + CLEAN PROFESSIONAL DESIGN ===
st.markdown("""
<style>
.stApp {
    background: 
        linear-gradient(135deg, #f8fbff 0%, #eef5ff 30%, #e0ecff 60%, #d0e2ff 100%),
        radial-gradient(circle at 15% 85%, rgba(200, 220, 255, 0.6), transparent 40%),
        radial-gradient(circle at 85% 20%, rgba(180, 210, 255, 0.5), transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(240, 248, 255, 0.7), transparent 60%),
        radial-gradient(circle at 30% 70%, rgba(255, 255, 255, 0.4), transparent 30%),
        radial-gradient(circle at 70% 60%, rgba(220, 235, 255, 0.4), transparent 35%);
    background-attachment: fixed;
    background-blend-mode: screen;
    color: #1e293b;
    padding-top: 0.5rem;
    position: relative;
    overflow: hidden;
}

/* Subtle floating orbs to mimic the 3D icons */
.stApp::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(circle at 10% 90%, #e8edff 8px, transparent 9px),
        radial-gradient(circle at 20% 70%, #ffffff 12px, transparent 13px),
        radial-gradient(circle at 80% 15%, #e0e7ff 10px, transparent 11px),
        radial-gradient(circle at 60% 80%, #d0d8ff 15px, transparent 16px),
        radial-gradient(circle at 40% 30%, #f0f4ff 11px, transparent 12px),
        radial-gradient(circle at 85% 60%, #ffffff 9px, transparent 10px),
        radial-gradient(circle at 30% 20%, #c8d4ff 14px, transparent 15px);
    background-size: 300px 300px, 250px 250px, 280px 280px, 320px 320px, 260px 260px, 240px 240px, 290px 290px;
    background-position: 10% 90%, 25% 65%, 80% 10%, 55% 75%, 45% 35%, 90% 55%, 35% 25%;
    opacity: 0.25;
    animation: float-orbs 40s ease-in-out infinite;
}

@keyframes float-orbs {
    0%, 100% { transform: translateY(0) translateX(0); }
    50% { transform: translateY(-40px) translateX(30px); }
}

#MainMenu, footer, header {visibility: hidden;}

.block-container {
    padding-top: 1rem !important;
}

.header-container {
    background: rgba(255, 255, 255, 0.95);
    padding: 1.2rem 1.5rem;
    text-align: center;
    border-radius: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.08);
    margin: 0 1.5rem 1.8rem 1.5rem;
    border-bottom: 4px solid #3b82f6;
    backdrop-filter: blur(8px);
}

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1e40af;
    margin: 0;
    letter-spacing: -0.6px;
}

.subtitle {
    font-size: 1.1rem;
    color: #475569;
    margin-top: 0.6rem;
    margin-bottom: 0;
    font-weight: 500;
}

.col-header {
    padding: 10px 16px;
    border-radius: 14px 14px 0 0;
    color: white;
    font-weight: 700;
    font-size: 0.95rem;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
.col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
.col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
.col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }

.col-body {
    background: white;
    border-radius: 0 0 14px 14px;
    padding: 12px;
    min-height: 520px;
    max-height: 620px;
    overflow-y: auto;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
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

# === TITLE ===
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# === RSS FEEDS & SOURCE TO CATEGORY MAPPING ===
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

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco",
    "Light Reading": "telco",
    "Fierce Telecom": "telco",
    "RCR Wireless": "telco",
    "Mobile World Live": "telco",
    "ET Telecom": "telco",
    "Netcracker Press": "telco",
    "Netcracker News": "telco",
    "Amdocs LinkedIn": "telco",
    "Variety": "ott",
    "Hollywood Reporter": "ott",
    "Deadline": "ott",
    "Digital TV Europe": "ott",
    "Advanced Television": "ott",
    "ESPN": "sports",
    "BBC Sport": "sports",
    "Front Office Sports": "sports",
    "Sportico": "sports",
    "SportsPro": "sports",
    "TechCrunch": "technology",
    "The Verge": "technology",
    "Wired": "technology",
    "Ars Technica": "technology",
    "VentureBeat": "technology",
    "ZDNet": "technology",
    "Engadget": "technology",
    "Techmeme": "technology",
}

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
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
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
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
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                categorized[category].append(item)

    # Sort each category by date (newest first)
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
        # Netcracker priority highlight
        categorized[cat] = sorted(
            categorized[cat],
            key=lambda x: -100 if "netcracker" in (x["title"] + x.get("summary", "")).lower() else 0,
            reverse=True
        )[:50]

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
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        is_netcracker = "netcracker" in (item["title"] + item.get("summary", "")).lower()
        card_class = "news-card-priority" if is_netcracker else "news-card"
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    if not items:
        cards = '<div style="text-align:center;color:#94a3b8;padding:30px;">No recent news</div>'
    return f'<div class="col-body">{cards}</div>'

# === INSTANT LOADING MESSAGE ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Powering up the latest insights...<br><small>Please wait a moment</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]
for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)
